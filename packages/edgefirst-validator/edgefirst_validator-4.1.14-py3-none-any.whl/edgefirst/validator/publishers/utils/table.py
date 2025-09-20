from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from edgefirst.validator.metrics import Metrics, MultitaskMetrics
    from edgefirst.validator.evaluators import CombinedParameters


def parameters_table(parameters: CombinedParameters) -> str:
    """
    Formats the parameters object into a string table.

    Parameters
    ----------
    parameters: CombinedParameters
        This contains the model, validation, and dataset parameters
        set from the command line.

    Returns
    -------
    str
        The formatted parameters as a string table.
    """

    if parameters.model.common.with_boxes:
        table = \
            f"""    +--------------------------------------------------+
        |     engine: {str(parameters.model.engine).ljust(37)}|
        |     NMS: {str(parameters.model.nms).ljust(40)}|
        |     NMS max detections: {str(parameters.model.max_detections).ljust(25)}|
        |     NMS IoU threshold: {str(parameters.model.iou_threshold).ljust(26)}|
        |     NMS score threshold: {str(parameters.model.score_threshold).ljust(24)}|
        |     validation IoU threshold: {str(parameters.validation.iou_threshold).ljust(19)}|
        |     validation Score threshold: {str(parameters.validation.score_threshold).ljust(17)}|
        |     normalization: {str(parameters.model.common.norm).ljust(30)}|
        |     preprocessing: {str(parameters.model.common.preprocessing).ljust(30)}|
        |     warmup: {str(parameters.model.warmup).ljust(37)}|
        |     metric: {str(parameters.validation.metric).ljust(37)}|"""
    else:
        table = \
            f"""    +--------------------------------------------------+
        |     engine: {str(parameters.model.engine).ljust(37)}|
        |     normalization: {str(parameters.model.common.norm).ljust(30)}|
        |     preprocessing: {str(parameters.model.common.preprocessing).ljust(30)}|
        |     warmup: {str(parameters.model.warmup).ljust(37)}|"""

    if parameters.validation.metric == "centerpoint":
        table += f"""
        |     matching leniency: {str(parameters.validation.metric).ljust(26)}|
    """

    if parameters.validation.clamp_boxes:
        table += f"""
        |     box clamp dimensions: {str(parameters.validation.clamp_boxes).ljust(23)}|
        |     box ignore dimensions: {str(parameters.validation.ignore_boxes).ljust(22)}|
    """

    if parameters.model.common.with_masks:
        table += f"""
        |     include background: {str(parameters.validation.include_background).ljust(25)}|
    """

    table += \
        """
        +--------------------------------------------------+
    """
    return table


def timings_table(timings: dict) -> str:
    """
    Formats the dictionary timings summary into a string table.

    Parameters
    ----------
    timings: dict
        This contains the timing information formatting in the following.

        .. code-block:: python

            {
                'min_read_time': minimum time to read the input,
                'max_read_time': maximum time to read the input,
                'min_load_time': minimum time to preprocess the input,
                'max_load_time': maximum time to preprocess the input,
                'min_backbone_time': minimum time to run the model,
                'max_backbone_time': maximum time to run the model,
                'min_decode_time': minimum time to decode the outputs,
                'max_decode_time': maximum time to decode the outputs,
                'min_box_time': minimum time to process the outputs,
                'max_box_time': maximum time to process the outputs,
                'avg_read_time': average time to read the input,
                'avg_load_time': average time to preprocess the input,
                'avg_backbone_time': average time to run the model,
                'avg_decode_time': average time to decode the outputs,
                'avg_box_time': average time to process the outputs,
            }

    Returns
    -------
    str
        The formatted timings in a table in milliseconds.
    """
    timings = {k: str(round(v, 2)) for k, v in timings.items()}

    table = f"""
    +----------------------------------------------------------+
    |  Read Time (ms)  |  Load Time (ms)  | Backbone Time (ms) |
    +------------------+------------------+--------------------+
    |  Min: {timings.get('min_read_time').ljust(11)}|  Min: {timings.get('min_load_time').ljust(11)}| Min: {timings.get('min_backbone_time').ljust(14)}|
    |  Max: {timings.get('max_read_time').ljust(11)}|  Max: {timings.get('max_load_time').ljust(11)}| Max: {timings.get('max_backbone_time').ljust(14)}|
    |  Avg: {timings.get('avg_read_time').ljust(11)}|  Avg: {timings.get('avg_load_time').ljust(11)}| Avg: {timings.get('avg_backbone_time').ljust(14)}|
    +------------------+---------+--------+--------------------+
    |      Decode Time (ms)      |      Box Time (ms)          |
    +----------------------------+-----------------------------+
    |      Min: {timings.get('min_decode_time').ljust(17)}|      Min: {timings.get('min_box_time').ljust(18)}|
    |      Max: {timings.get('max_decode_time').ljust(17)}|      Max: {timings.get('max_box_time').ljust(18)}|
    |      Avg: {timings.get('avg_decode_time').ljust(17)}|      Avg: {timings.get('avg_box_time').ljust(18)}|
    +----------------------------+-----------------------------+
    """
    return table


def multitask_table(metrics: MultitaskMetrics,
                    parameters: CombinedParameters) -> str:
    """
    Formats the multitask metrics into a string table.

    Parameters
    ----------
    metrics: MultitaskMetrics
        This is a container for both detection and segmentation metrics.
    parameters: CombinedParameters
        Thisi contains the model, validation, and dataset parameters
        set from the command line.

    Returns
    -------
    str
        The formatted validation table showing the metrics, parameters,
        and model timings.
    """
    if parameters.validation.method in ["ultralytics", "yolov7"]:
        d_metrics = metrics.detection_metrics
        s_metrics = metrics.segmentation_metrics

        table = \
            f"""        +--------------------------------------------------+
        | Model: {str(d_metrics.model).ljust(42)}|
        | Dataset: {str(d_metrics.dataset).ljust(40)}|
        +--------------------------------------------------+
        |                DETECTION METRICS                 |
        +--------------------------------------------------+
        | Ground Truths: {str(d_metrics.ground_truths).ljust(34)}|
        | Predictions: {str(d_metrics.predictions).ljust(36)}|
        +---------------+-------------------+--------------+
        |               | Mean Precision    |{str(round(d_metrics.precision["mean"]*100, 2)).center(14)}|
        |               | mAP@0.5           |{str(round(d_metrics.precision["map"].get('0.50')*100, 2)).center(14)}|
        | Precision (%) | mAP@0.75          |{str(round(d_metrics.precision["map"].get('0.75')*100, 2)).center(14)}|
        |               | mAP@0.5-0.95      |{str(round(d_metrics.precision["map"].get('0.50:0.95')*100, 2)).center(14)}|
        +---------------+-------------------+--------------+
        | Recall (%)    | Mean Recall       |{str(round(d_metrics.recall["mean"]*100, 2)).center(14)}|
        +---------------+-------------------+--------------+
        | F1 Score (%)  | Mean F1           |{str(round(d_metrics.f1["mean"]*100, 2)).center(14)}|
        +---------------+-------------------+--------------+
        |               SEGMENTATION METRICS               |
        +--------------------------------------------------+
        |               | Mean Precision    |{str(round(s_metrics.precision["mean"]*100, 2)).center(14)}|
        |               | mAP@0.5           |{str(round(s_metrics.precision["map"].get('0.50')*100, 2)).center(14)}|
        | Precision (%) | mAP@0.75          |{str(round(s_metrics.precision["map"].get('0.75')*100, 2)).center(14)}|
        |               | mAP@0.5-0.95      |{str(round(s_metrics.precision["map"].get('0.50:0.95')*100, 2)).center(14)}|
        +---------------+-------------------+--------------+
        | Recall (%)    | Mean Recall       |{str(round(s_metrics.recall["mean"]*100, 2)).center(14)}|
        +---------------+-------------------+--------------+
        | F1 Score (%)  | Mean F1           |{str(round(s_metrics.f1["mean"]*100, 2)).center(14)}|
        +---------------+-------------------+--------------+
        """

    else:
        d_metrics = metrics.detection_metrics
        s_metrics = metrics.segmentation_metrics

        table = \
            f"""        +--------------------------------------------------+
        | Model: {str(d_metrics.model).ljust(42)}|
        | Dataset: {str(d_metrics.dataset).ljust(40)}|
        +--------------------------------------------------+
        |                DETECTION METRICS                 |
        +---------------+----------------+-----------------+
        | Ground Truths | True Positives | False Negatives |
        +---------------+----------------+-----------------+
        |{str(d_metrics.ground_truths).center(15)}|{str(d_metrics.tp).center(16)}|{str(d_metrics.fn).center(17)}|
        +-------------------------+------------------------+
        |    Classification FP    |    Localization FP     |
        +-------------------------+------------------------+
        |{str(d_metrics.cfp).center(25)}|{str(d_metrics.lfp).center(24)}|
        +---------------+---------+---------+--------------+
        |               | Overall Accuracy  |{str(round(d_metrics.accuracy["overall"]*100, 2)).center(14)}|
        |               | mACC@0.5          |{str(round(d_metrics.accuracy["macc"].get('0.50')*100, 2)).center(14)}|
        | Accuracy (%)  | mACC@0.75         |{str(round(d_metrics.accuracy["macc"].get('0.75')*100, 2)).center(14)}|
        |               | mACC@0.5-0.95     |{str(round(d_metrics.accuracy["macc"].get('0.50:0.95')*100, 2)).center(14)}|
        +---------------+-------------------+--------------+
        |               | Overall Precision |{str(round(d_metrics.precision["overall"]*100, 2)).center(14)}|
        |               | mAP@0.5           |{str(round(d_metrics.precision["map"].get('0.50')*100, 2)).center(14)}|
        | Precision (%) | mAP@0.75          |{str(round(d_metrics.precision["map"].get('0.75')*100, 2)).center(14)}|
        |               | mAP@0.5-0.95      |{str(round(d_metrics.precision["map"].get('0.50:0.95')*100, 2)).center(14)}|
        +---------------+-------------------+--------------+
        |               | Overall Recall    |{str(round(d_metrics.recall["overall"]*100, 2)).center(14)}|
        |               | mAR@0.5           |{str(round(d_metrics.recall["mar"].get('0.50')*100, 2)).center(14)}|
        | Recall (%)    | mAR@0.75          |{str(round(d_metrics.recall["mar"].get('0.75')*100, 2)).center(14)}|
        |               | mAR@0.5-0.95      |{str(round(d_metrics.recall["mar"].get('0.50:0.95')*100, 2)).center(14)}|
        +---------------+-------------------+--------------+
        |               SEGMENTATION METRICS               |
        +--------------------------------------------------+
        | Ground Truths: {str(s_metrics.ground_truths).ljust(34)}|
        | Predictions: {str(s_metrics.predictions).ljust(36)}|
        | Union: {str(s_metrics.union).ljust(42)}|
        +------------------------+-------------------------+
        |    True Predictions    |    False Predictions    |
        +------------------------+-------------------------+
        |{str(s_metrics.true_predictions).center(24)}|{str(s_metrics.false_predictions).center(25)}|
        +------------------------+-------------------------+
        | Overall Accuracy   (%) |{str(round(s_metrics.accuracy["overall"]*100, 2)).center(25)}|
        | Overall Precision  (%) |{str(round(s_metrics.precision["overall"]*100, 2)).center(25)}|
        | Overall Recall     (%) |{str(round(s_metrics.recall["overall"]*100, 2)).center(25)}|
        +------------------------+-------------------------+
        | Average Accuracy   (%) |{str(round(s_metrics.accuracy["mean"]*100, 2)).center(25)}|
        | Average Precision  (%) |{str(round(s_metrics.precision["mean"]*100, 2)).center(25)}|
        | Average Recall     (%) |{str(round(s_metrics.recall["mean"]*100, 2)).center(25)}|
        +------------------------+-------------------------+
        """

    if d_metrics.model.lower() != "model":
        table += timings_table(metrics.timings)
        table += parameters_table(parameters)

    return table


def detection_table(metrics: Metrics, parameters: CombinedParameters) -> str:
    """
    Formats the detection metrics into a string table.

    Parameters
    ----------
    metrics: Metrics
        This is the detection metrics computed during validation.
    parameters: CombinedParameters
        This contains the model, validation, and dataset parameters
        set from the command line.

    Returns
    -------
    str
        The formatted validation table showing the metrics, parameters,
        and model timings.
    """
    if parameters.validation.method in ["ultralytics", "yolov7"]:
        table = \
            f"""        +--------------------------------------------------+
        | Model: {str(metrics.model).ljust(42)}|
        | Dataset: {str(metrics.dataset).ljust(40)}|
        | Ground Truths: {str(metrics.ground_truths).ljust(34)}|
        | Predictions: {str(metrics.predictions).ljust(36)}|
        +---------------+-------------------+--------------+
        |               | Mean Precision    |{str(round(metrics.precision["mean"]*100, 2)).center(14)}|
        |               | mAP@0.5           |{str(round(metrics.precision["map"].get('0.50')*100, 2)).center(14)}|
        | Precision (%) | mAP@0.75          |{str(round(metrics.precision["map"].get('0.75')*100, 2)).center(14)}|
        |               | mAP@0.5-0.95      |{str(round(metrics.precision["map"].get('0.50:0.95')*100, 2)).center(14)}|
        +---------------+-------------------+--------------+
        | Recall (%)    | Mean Recall       |{str(round(metrics.recall["mean"]*100, 2)).center(14)}|
        +---------------+-------------------+--------------+
        | F1 Score (%)  | Mean F1           |{str(round(metrics.f1["mean"]*100, 2)).center(14)}|
        +---------------+-------------------+--------------+
    """

    else:
        table = \
            f"""        +--------------------------------------------------+
        | Model: {str(metrics.model).ljust(42)}|
        | Dataset: {str(metrics.dataset).ljust(40)}|
        +---------------+----------------+-----------------+
        | Ground Truths | True Positives | False Negatives |
        +---------------+----------------+-----------------+
        |{str(metrics.ground_truths).center(15)}|{str(metrics.tp).center(16)}|{str(metrics.fn).center(17)}|
        +-------------------------+------------------------+
        |    Classification FP    |    Localization FP     |
        +-------------------------+------------------------+
        |{str(metrics.cfp).center(25)}|{str(metrics.lfp).center(24)}|
        +---------------+---------+---------+--------------+
        |               | Overall Accuracy  |{str(round(metrics.accuracy["overall"]*100, 2)).center(14)}|
        |               | mACC@0.5          |{str(round(metrics.accuracy["macc"].get('0.50')*100, 2)).center(14)}|
        | Accuracy (%)  | mACC@0.75         |{str(round(metrics.accuracy["macc"].get('0.75')*100, 2)).center(14)}|
        |               | mACC@0.5-0.95     |{str(round(metrics.accuracy["macc"].get('0.50:0.95')*100, 2)).center(14)}|
        +---------------+-------------------+--------------+
        |               | Overall Precision |{str(round(metrics.precision["overall"]*100, 2)).center(14)}|
        |               | mAP@0.5           |{str(round(metrics.precision["map"].get('0.50')*100, 2)).center(14)}|
        | Precision (%) | mAP@0.75          |{str(round(metrics.precision["map"].get('0.75')*100, 2)).center(14)}|
        |               | mAP@0.5-0.95      |{str(round(metrics.precision["map"].get('0.50:0.95')*100, 2)).center(14)}|
        +---------------+-------------------+--------------+
        |               | Overall Recall    |{str(round(metrics.recall["overall"]*100, 2)).center(14)}|
        |               | mAR@0.5           |{str(round(metrics.recall["mar"].get('0.50')*100, 2)).center(14)}|
        | Recall (%)    | mAR@0.75          |{str(round(metrics.recall["mar"].get('0.75')*100, 2)).center(14)}|
        |               | mAR@0.5-0.95      |{str(round(metrics.recall["mar"].get('0.50:0.95')*100, 2)).center(14)}|
        +---------------+-------------------+--------------+
    """

    if metrics.model.lower() != "model":
        table += timings_table(metrics.timings)
        table += parameters_table(parameters)

    return table


def segmentation_table(metrics: Metrics,
                       parameters: CombinedParameters) -> str:
    """
    Formats the segmentation metrics into a string table.

    Parameters
    ----------
    metrics: Metrics
        This is the segmentation metrics computed during validation.
    parameters: CombinedParameters
        This contains the model, validation, and dataset parameters
        set from the command line.

    Returns
    -------
    str
        The formatted validation table showing the metrics, parameters,
        and model timings.
    """

    table = \
        f"""        +--------------------------------------------------+
        | Model: {metrics.model.ljust(42)}|
        | Dataset: {metrics.dataset.ljust(40)}|
        | Engine: {parameters.model.engine.ljust(41)}|
        | Ground Truths: {str(metrics.ground_truths).ljust(34)}|
        | Predictions: {str(metrics.predictions).ljust(36)}|
        | Union: {str(metrics.union).ljust(42)}|
        +------------------------+-------------------------+
        |    True Predictions    |    False Predictions    |
        +------------------------+-------------------------+
        |{str(metrics.true_predictions).center(24)}|{str(metrics.false_predictions).center(25)}|
        +------------------------+-------------------------+
        | Overall Accuracy   (%) |{str(round(metrics.accuracy["overall"]*100, 2)).center(25)}|
        | Overall Precision  (%) |{str(round(metrics.precision["overall"]*100, 2)).center(25)}|
        | Overall Recall     (%) |{str(round(metrics.recall["overall"]*100, 2)).center(25)}|
        +------------------------+-------------------------+
        | Average Accuracy   (%) |{str(round(metrics.accuracy["mean"]*100, 2)).center(25)}|
        | Average Precision  (%) |{str(round(metrics.precision["mean"]*100, 2)).center(25)}|
        | Average Recall     (%) |{str(round(metrics.recall["mean"]*100, 2)).center(25)}|
        +------------------------+-------------------------+
    """

    if metrics.model.lower() != "model":
        table += timings_table(metrics.timings)
        table += parameters_table(parameters)
    return table


def pose_table(metrics: Metrics, parameters: CombinedParameters) -> str:
    """
    Formats the head pose metrics into a string table.

    Parameters
    ----------
    metrics: Metrics
        This is the pose metrics computed during validation.
    parameters: CombinedParameters
        This contains the model, validation, and dataset parameters
        set from the command line.

    Returns
    -------
    str
        The formatted validation table showing the metrics, parameters,
        and model timings.
    """

    if len(metrics.angles_mae) == 3:
        table = \
            f"""        +--------------------------------------------------+
        | Model: {metrics.model.ljust(42)}|
        | Dataset: {metrics.dataset.ljust(40)}|
        +--------------+-------+---------------------------+
        |              | Roll  |{str(round(metrics.angles_mae[0],2)).center(27)}|
        |     Mean     +-------+---------------------------+
        |   Absolute   | Pitch |{str(round(metrics.angles_mae[1], 2)).center(27)}|
        |     Error    +-------+---------------------------+
        |              | Yaw   |{str(round(metrics.angles_mae[2], 2)).center(27)}|
        +--------------+-------+---------------------------+
    """

    # Quaternion angles
    elif len(metrics.angles_mae) == 4:
        table = \
            f"""        +--------------------------------------------------+
        | Model: {metrics.model.ljust(42)}|
        | Dataset: {metrics.dataset.ljust(40)}|
        +--------------+-------+---------------------------+
        |              | real  |{str(round(metrics.angles_mae[0],2)).center(27)}|
        |              +-------+---------------------------+
        |     Mean     |   i   |{str(round(metrics.angles_mae[1], 2)).center(27)}|
        |   Absolute   +-------+---------------------------+
        |     Error    |   j   |{str(round(metrics.angles_mae[2], 2)).center(27)}|
        |              +-------+---------------------------+
        |              |   k   |{str(round(metrics.angles_mae[3], 2)).center(27)}|
        +--------------+-------+---------------------------+
    """

    else:
        table = \
            f"""        +--------------------------------------------------+
        | Model: {metrics.model.ljust(42)}|
        | Dataset: {metrics.dataset.ljust(40)}|
        +--------------------------------------------------+
        |               Mean Absolute Error                |
        +--------------------------------------------------+
    """
        for i in range(len(metrics.angles_mae)):
            table_summary += \
                f"""
        | angle_{i} |{str(round(metrics.angles_mae[i], 2)).center(38)}|
        +-----------+--------------------------------------+
    """

    if metrics.model.lower() != "model":
        table += timings_table(metrics.timings)

    return table
