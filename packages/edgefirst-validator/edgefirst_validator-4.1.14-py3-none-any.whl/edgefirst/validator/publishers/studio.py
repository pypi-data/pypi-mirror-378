import os
import glob
import json
from typing import Union

from edgefirst_client import Client


class StudioPublisher:
    """
    Publishes the plots to EdgeFirst Studio.

    Parameters
    ----------
    json_path: str
        The path to store the ApexCharts JSON files.
    session_id: Union[int, str]
        The validation session ID in EdgeFirst Studio.
    client: Client
        The client interface to post requests to
        the EdgeFirst Studio API.
    """

    def __init__(
        self,
        json_path: str,
        session_id: Union[int, str],
        client: Client
    ):
        self.json_path = json_path
        self.session_id = session_id
        self.client = client
        self.session = self.client.validation_session(session_id=session_id)

    def update_stage(
        self,
        stage: str,
        status: str,
        message: str,
        percentage: int
    ):
        """
        Sets the stage reported in EdgeFirst Studio.

        Parameters
        ----------
        stage: str
            This is the current stage of the progress.
        status: str
            The status of the runtime. This can be set to
            'complete', 'error', or 'running'.
        message: str
            Any message for more description on the stage.
        percentage: int
            The percentage of the stage with a total of 100.
        """
        self.client.update_stage(
            task_id=self.session.task.id,
            stage=stage,
            status=status,
            message=message,
            percentage=percentage
        )

    def save_json(self, filename: str, plot: dict):
        """
        Save the JSON file containing data
        for the validation plots.

        Parameters
        ----------
        filename: str
            The name of the file.
        plot: dict
            The dictionary with the data
            for the plots.
        """
        with open(os.path.join(self.json_path, filename), 'w') as fp:
            json.dump(plot, fp)

    def post_plots(self):
        """
        Post the JSON files with the validation metrics
        to EdgeFirst Studio.
        """

        files = glob.glob(os.path.join(self.json_path, "*.json"))
        files = [(os.path.basename(file), file) for file in files]

        self.session.upload(
            client=self.client,
            files=files
        )

    def post_metrics(self, metrics: dict):
        """
        Post the final metrics reported in validator.

        Parameters
        ----------
        metrics: dict
            This is a container for the metrics.
        """
        self.session.set_metrics(
            client=self.client,
            metrics=metrics
        )
