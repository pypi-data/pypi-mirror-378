"""
Neural-symbolic matching models module.

This module contains functionality for instantiating, training, and evaluating
neural-symbolic matching models
"""

from neer_match.axiom_generator import AxiomGenerator
from neer_match.data_generator import DataGenerator
from neer_match.matching_model_tools import _evaluate_loop, _suggest
from neer_match.metrics import (
    PrecisionMetric,
    RecallMetric,
    AccuracyMetric,
    F1Metric,
    MCCMetric,
)
from neer_match.record_pair_network import RecordPairNetwork
from neer_match.similarity_map import SimilarityMap

import ltn
import pandas as pd
import tensorflow as tf
import typing


class NSMatchingModel(tf.keras.Model):
    """A neural-symbolic matching model class.

    Attributes:
        record_pair_network (RecordPairNetwork): The record pair network.
        bce (tf.keras.losses.Loss): The training loss function (binary cross-entropy,
            see :func:`tensorflow.keras.losses.BinaryCrossentropy`).
        optimizer (tensorflow.keras.optimizers.Optimizer): The optimizer used for
            training.
    """

    def __init__(
        self,
        similarity_map: SimilarityMap,
        initial_feature_width_scales: typing.Union[int, typing.List[int]] = 10,
        feature_depths: typing.Union[int, typing.List[int]] = 2,
        initial_record_width_scale: int = 10,
        record_depth: int = 4,
        **kwargs,
    ) -> None:
        """Initialize a neural-symbolic matching learning matching model.

        Generate a record pair network from the passed similarity map. The input
        arguments are passed to the record pair network (see
        :class:`.RecordPairNetwork`).

        The class uses a custom training loop with neural-symbolic (or hybrid) loss
        function. It does not inherit from :class:`tensorflow.keras.Model`, but to
        provide a consistent interface with the deep learning matching model, it
        implements the same methods.

        Args:
            similarity_map: A similarity map object.
            initial_feature_width_scales: The initial width scales of the feature
                networks.
            feature_depths: The depths of the feature networks.
            initial_record_width_scale: The initial width scale of the record network.
            record_depth: The depth of the record network.
        """
        super().__init__(**kwargs)
        self.record_pair_network = RecordPairNetwork(
            similarity_map,
            initial_feature_width_scales=initial_feature_width_scales,
            feature_depths=feature_depths,
            initial_record_width_scale=initial_record_width_scale,
            record_depth=record_depth,
        )

    def compile(
        self,
        optimizer: tf.keras.optimizers.Optimizer = tf.keras.optimizers.Adam(
            learning_rate=1e-4
        ),
    ) -> None:
        """Compile the model.

        Args:
            optimizer: The optimizer used for training.
        """
        self.bce = tf.keras.losses.BinaryCrossentropy()
        self.optimizer = optimizer
        features = [
            tf.random.normal((1, size), dtype=tf.float32)
            for size in self.record_pair_network.similarity_map.association_sizes()
        ]
        self.record_pair_network(features)

    def _make_axioms(self, data_generator: DataGenerator) -> typing.Callable:
        axiom_generator = AxiomGenerator(data_generator)
        field_predicates = [
            ltn.Predicate(f) for f in self.record_pair_network.field_networks
        ]
        record_predicate = ltn.Predicate(self.record_pair_network)
        is_positive = ltn.Predicate.Lambda(lambda x: x > 0.0)

        @tf.function
        def axioms(features: dict[str, tf.Tensor], labels: tf.Tensor) -> tf.Tensor:
            propositions = []

            y = ltn.Variable("y", labels)
            x = [
                ltn.Variable(f"x{i}", features[key])
                for i, key in enumerate(features.keys())
            ]

            stmt = axiom_generator.ForAll(
                [x[0], y], field_predicates[0](x[0]), mask=is_positive(y)
            )
            for i, F in enumerate(field_predicates[1:]):
                stmt = axiom_generator.Or(
                    stmt,
                    axiom_generator.ForAll(
                        [x[i + 1], y], F(x[i + 1]), mask=is_positive(y)
                    ),
                )
            propositions.append(stmt)
            stmt = axiom_generator.ForAll(
                [*x, y], record_predicate(x), mask=is_positive(y)
            )
            propositions.append(stmt)

            stmt = axiom_generator.ForAll(
                [x[0], y],
                axiom_generator.Not(field_predicates[0](x[0])),
                mask=axiom_generator.Not(is_positive(y)),
            )
            for i, F in enumerate(field_predicates[1:]):
                stmt = axiom_generator.Or(
                    stmt,
                    axiom_generator.ForAll(
                        [x[i + 1], y],
                        axiom_generator.Not(F(x[i + 1])),
                        mask=axiom_generator.Not(is_positive(y)),
                    ),
                )
            propositions.append(stmt)
            stmt = axiom_generator.ForAll(
                [*x, y],
                axiom_generator.Not(record_predicate(x)),
                mask=axiom_generator.Not(is_positive(y)),
            )
            propositions.append(stmt)

            kb = axiom_generator.FormAgg(propositions)
            sat = kb.tensor
            return sat

        return axioms

    def __for_epoch(
        self,
        data_generator: DataGenerator,
        loss_clb: typing.Callable,
        trainable_variables: typing.List[tf.Variable],
        verbose: int = 1,
        metrics: typing.Optional[typing.Sequence[tf.keras.metrics.Metric]] = None,
    ) -> dict:
        no_batches = len(data_generator)
        pb_size = 60
        logs = {
            "no_batches": no_batches,
            "TP": 0,
            "FP": 0,
            "TN": 0,
            "FN": 0,
            "BCE": 0,
            "Sat": 0,
            "Loss": 0,
            "F1": None,
            "MCC": None,
            "Accuracy": None,
            "Precision": None,
            "Recall": None,
        }

        for i, (features, labels) in enumerate(data_generator):
            if verbose > 0:
                pb_step = int((i + 1) / no_batches * pb_size)
                pb = "=" * pb_step + "." * (pb_size - pb_step)
                print(f"\r[{pb}] {i + 1}/{no_batches}", end="", flush=True)

            with tf.GradientTape() as tape:
                batch_loss, batch_logs = loss_clb(features, labels)
            grads = tape.gradient(batch_loss, trainable_variables)
            self.optimizer.apply_gradients(zip(grads, trainable_variables))

            preds = batch_logs["Predicted"]
            preds = tf.reshape(preds, preds.shape[0])

            # running counts
            logs["TP"] += tf.reduce_sum(tf.round(preds) * labels)
            logs["FP"] += tf.reduce_sum(tf.round(preds) * (1.0 - labels))
            logs["TN"] += tf.reduce_sum((1.0 - tf.round(preds)) * (1.0 - labels))
            logs["FN"] += tf.reduce_sum((1.0 - tf.round(preds)) * labels)
            logs["BCE"] += batch_logs["BCE"]
            logs["Sat"] += batch_logs["Sat"]
            if "ASat" in batch_logs:
                if "ASat" not in logs:
                    logs["ASat"] = batch_logs["ASat"]
                else:
                    logs["ASat"] += batch_logs["ASat"]
            logs["Loss"] += batch_loss

            # update optional custom metrics
            if metrics:
                for m in metrics:
                    m.update_state(labels, preds)

        logs["Sat"] /= no_batches
        if "ASat" in logs:
            logs["ASat"] /= no_batches

        if verbose > 0:
            print("\r", end="", flush=True)

        # Fill derived metrics at the end
        if metrics:
            m = {mtr.name: mtr for mtr in metrics}
            if "accuracy" in m:
                logs["Accuracy"] = m["accuracy"].result()
            if "precision" in m:
                logs["Precision"] = m["precision"].result()
            if "recall" in m:
                logs["Recall"] = m["recall"].result()
            if "f1" in m:
                logs["F1"] = m["f1"].result()
            if "mcc" in m:
                logs["MCC"] = m["mcc"].result()
        else:
            # compute from TP/FP/TN/FN (kept for completeness)
            tp = tf.cast(logs["TP"], tf.float32)
            fp = tf.cast(logs["FP"], tf.float32)
            tn = tf.cast(logs["TN"], tf.float32)
            fn = tf.cast(logs["FN"], tf.float32)

            # NaN if undefined
            precision = tp / (tp + fp)
            recall = tp / (tp + fn)
            logs["Precision"] = precision
            logs["Recall"] = recall
            logs["F1"] = (2.0 * precision * recall) / (precision + recall)
            logs["MCC"] = (tp * tn - fp * fn) / tf.sqrt(
                (tp + fp) * (tp + fn) * (tn + fp) * (tn + fn)
            )
            logs["Accuracy"] = (tp + tn) / (tp + tn + fp + fn)

        return logs

    def __make_loss(
        self, axioms: typing.Callable, satisfiability_weight: float
    ) -> typing.Callable:
        @tf.function
        def loss_clb(
            features: dict[str, tf.Tensor], labels: tf.Tensor
        ) -> typing.Tuple[tf.Tensor, dict]:
            preds = self.record_pair_network(features)
            bce = self.bce(labels, preds)
            sat = axioms(features, labels)
            loss = (1.0 - satisfiability_weight) * bce + satisfiability_weight * (
                1.0 - sat
            )
            logs = {"BCE": bce, "Sat": sat, "Predicted": preds}
            return loss, logs

        return loss_clb

    def _training_loop_log_header(self) -> str:
        headers = ["Epoch", "BCE", "Recall", "Precision", "F1", "Sat", "MCC"]
        return "| " + " | ".join([f"{x:<10}" for x in headers]) + " |"

    def _training_loop_log_row(self, epoch: int, logs: dict) -> str:
        def _to_float(x):
            # accept python floats, numpy floats, or tf.Tensors
            if hasattr(x, "numpy"):
                x = x.numpy()
            return float(x)

        tp = logs["TP"]
        fp = logs["FP"]
        tn = logs["TN"]
        fn = logs["FN"]

        # compute as tensors to preserve NaN when denominators are zero
        tp = tf.cast(tp, tf.float32)
        fp = tf.cast(fp, tf.float32)
        tn = tf.cast(tn, tf.float32)
        fn = tf.cast(fn, tf.float32)

        recall = tp / (tp + fn)
        precision = tp / (tp + fp)
        f1 = (2.0 * precision * recall) / (precision + recall)
        mcc = (tp * tn - fp * fn) / tf.sqrt(
            (tp + fp) * (tp + fn) * (tn + fp) * (tn + fn)
        )

        bce = logs["BCE"]
        sat = logs["Sat"]

        values = [
            _to_float(bce),
            _to_float(recall),
            _to_float(precision),
            _to_float(f1),
            _to_float(mcc),
            _to_float(sat),
        ]
        row = f"| {epoch:<10} | " + " | ".join(f"{v:<10.4f}" for v in values) + " |"
        return row

    def _training_loop_log_end(self, epoch: int, logs: dict) -> str:
        return (
            f"Training finished at Epoch {epoch} with "
            f"DL loss {logs['BCE'].numpy():.4f} and "
            f"Sat {logs['Sat'].numpy():.4f}"
        )

    def _training_loop(
        self,
        data_generator: DataGenerator,
        loss_clb: typing.Callable,
        trainable_variables: typing.List[tf.Variable],
        epochs: int,
        verbose: int,
        log_mod_n: int,
    ) -> None:
        if verbose > 0:
            print(self._training_loop_log_header())

        for epoch in range(epochs):
            logs = self.__for_epoch(
                data_generator,
                loss_clb,
                trainable_variables,
                verbose=verbose - 1,
            )
            if verbose > 0 and epoch % log_mod_n == 0:
                print(self._training_loop_log_row(epoch, logs))
        if verbose > 0:
            print(self._training_loop_log_end(epoch, logs))

    def fit(
        self,
        left: pd.DataFrame,
        right: pd.DataFrame,
        matches: pd.DataFrame,
        epochs: int,
        mismatch_share: float = 0.1,
        satisfiability_weight: float = 1.0,
        verbose: int = 1,
        log_mod_n: int = 1,
        **kwargs,
    ) -> None:
        """Fit the model.

        Construct a data generator from the input data frames using the similarity map
        with which the model was initialized and fit the model.

        The model is trained using a custom training loop. The loss can either be purely
        defined using fuzzy logic axioms (default case with satisfiability weight 1.0)
        or as a weighted sum of binary cross-entropy and satisfiability loss (by setting
        the satisfiability weight to a value between 0 and 1).

        Args:
            left: The left data frame.
            right: The right data frame.
            matches: The matches data frame.
            epochs: The number of epochs to train.
            mismatch_share: The mismatch share.
            satisfiability_weight: The weight of the satisfiability loss.
            verbose: The verbosity level.
            log_mod_n: The log modulo.
            **kwargs: Additional keyword arguments passed to the data generator.
        """
        if not isinstance(epochs, int) or epochs < 1:
            raise ValueError("Epochs must be an integer greater than 0")
        if satisfiability_weight < 0.0 or satisfiability_weight > 1.0:
            raise ValueError("Satisfiability weight must be between 0 and 1")
        if not isinstance(verbose, int):
            raise ValueError("Verbose must be an integer")
        if not isinstance(log_mod_n, int) or log_mod_n < 1:
            raise ValueError("Log mod n must be an integer greater than 0")
        # The remaining arguments are validated in the DataGenerator

        data_generator = DataGenerator(
            self.record_pair_network.similarity_map,
            left,
            right,
            matches,
            mismatch_share=mismatch_share,
            **kwargs,
        )

        axioms = self._make_axioms(data_generator)
        loss_clb = self.__make_loss(axioms, satisfiability_weight)

        trainable_variables = self.record_pair_network.trainable_variables
        self._training_loop(
            data_generator, loss_clb, trainable_variables, epochs, verbose, log_mod_n
        )

    def compile_as_DL(
        self,
        optimizer=None,
        loss=None,
        metrics=None,
        *,
        threshold: float = 0.5,
        **kwargs,
    ):
        """
        Compile the NS model in plain DL mode using the same defaults and
        extended metrics as DLMatchingModel.compile.

        Args:
            optimizer: Optimizer to use. Defaults to Adam(1e-4).
            loss: Loss function. Defaults to BinaryCrossentropy().
            metrics: If None, uses extended metrics (accuracy, precision, recall,
                     F1, MCC). If a list is provided, it is used as-is.
            threshold: Threshold for binary metrics (default 0.5).
            **kwargs: Passed to tf.keras.Model.compile.
        """
        if optimizer is None:
            optimizer = tf.keras.optimizers.Adam(learning_rate=1e-4)
        if loss is None:
            loss = tf.keras.losses.BinaryCrossentropy()

        # Save for consistency if you later need it elsewhere
        self._threshold = float(threshold)

        if metrics is None:
            metrics = [
                AccuracyMetric(name="accuracy", threshold=threshold),
                PrecisionMetric(name="precision", threshold=threshold),
                RecallMetric(name="recall", threshold=threshold),
                F1Metric(name="f1", threshold=threshold),
                MCCMetric(name="mcc", threshold=threshold),
            ]

        return super().compile(
            optimizer=optimizer, loss=loss, metrics=metrics, **kwargs
        )

    def call(self, inputs: typing.Dict[str, tf.Tensor]) -> tf.Tensor:
        """Call the model on inputs."""
        return self.record_pair_network(inputs)

    def evaluate(
        self,
        left: pd.DataFrame,
        right: pd.DataFrame,
        matches: pd.DataFrame,
        batch_size: int = 16,
        mismatch_share: float = 1.0,
        satisfiability_weight: float = 1.0,
        use_axioms: bool = True,
        **kwargs,
    ) -> dict:
        """Evaluate the model.

        Construct a data generator from the input data frames using the similarity map
        with which the model was initialized and evaluate the model. It returns a
        dictionary with evaluation metrics.

        Args:
            left: The left data frame.
            right: The right data frame.
            matches: The matches data frame.
            batch_size: Batch size.
            mismatch_share: The mismatch share.
            satisfiability_weight: The weight of the satisfiability loss.
            use_axioms: Indicator if satisfiability score should be calculated.
            **kwargs: Additional keyword arguments for `super().evaluate`.
        """
        data_generator = DataGenerator(
            self.record_pair_network.similarity_map,
            left,
            right,
            matches,
            mismatch_share=mismatch_share,
            batch_size=batch_size,
            shuffle=False,
        )

        if not use_axioms:
            self.compile_as_DL(threshold=getattr(self, "_threshold", 0.5))
            return _evaluate_loop(
                forward_fn=self.record_pair_network,
                generator=data_generator,
                base_loss_fn=self.loss,
                threshold=getattr(self, "_threshold", 0.5),
                axioms=None,
            )
        else:
            axioms = self._make_axioms(data_generator)
            # base BCE for the hybrid component; could also be another loss if desired
            base_loss_fn = getattr(self, "bce", tf.keras.losses.BinaryCrossentropy())
            return _evaluate_loop(
                forward_fn=self.record_pair_network,
                generator=data_generator,
                base_loss_fn=base_loss_fn,
                threshold=getattr(self, "_threshold", 0.5),
                axioms=axioms,
                satisfiability_weight=satisfiability_weight,
            )

    def predict_from_generator(self, generator: DataGenerator) -> tf.Tensor:
        """Generate model predictions from a generator.

        Args:
            generator: The data generator.
        """
        if isinstance(generator, DataGenerator):
            preds = self.record_pair_network(generator[0])
        else:
            preds = self.record_pair_network(generator)
        return preds

    def predict(
        self, left: pd.DataFrame, right: pd.DataFrame, batch_size: int = 16
    ) -> tf.Tensor:
        """Generate model predictions.

        Construct a data generator from the input data frames using the
        similarity map with which the model was initialized and generate predictions.

        Args:
            left: The left data frame.
            right: The right data frame.
            batch_size: Batch size.
        """
        generator = DataGenerator(
            self.record_pair_network.similarity_map,
            left,
            right,
            mismatch_share=1.0,
            batch_size=batch_size,
            shuffle=False,
        )
        return self.predict_from_generator(generator)

    def suggest(
        self, left: pd.DataFrame, right: pd.DataFrame, count: int, batch_size=16
    ) -> pd.DataFrame:
        """Generate model suggestions.

        Construct a data generator from the input data frames using the similarity map
        with which the model was initialized and generate suggestions.

        Args:
            left: The left data frame.
            right: The right data frame.
            count: The number of suggestions to generate.
            batch_size: Batch size.
        """
        return _suggest(self, left, right, count, batch_size=batch_size)

    @property
    def similarity_map(self) -> SimilarityMap:
        """Similarity Map of the Model."""
        return self.record_pair_network.similarity_map
