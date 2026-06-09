"""
simulation_ftp_images.py
------------------------
This script replays batches of images that were previously saved to a local FTP folder
by an ifm O2x5xx sensor (FTP-push feature) and feeds them back into the sensor's
simulation mode.

Workflow overview:
  1. Scan a local FTP folder for JPEG images pushed by the sensor.
  2. Group the images into "batches" based on the encoded filename information
     (timestamp, sensor name, application name, image index, and expected PASS/FAIL result).
  3. Connect to the sensor via RPC (configuration) and PCIC (result output).
  4. Switch the sensor to simulation mode.
  5. For every batch, send the ordered image sequence to the sensor and read back the
     application result.
  6. Compare the application result against the PASS/FAIL label that was stored in the
     filename and print a warning if the two values do not match.

Expected filename format (set in the sensor's FTP-push configuration):
    <YYYYMMDD>_<HHMMSS>_<ms>_<SensorName>_<ApplicationName>_<ImageIndex>_<PASS|FAIL>.jpg
    Example: 20000101_002456_106_Demo Sensor_Advanced application_01_PASS.jpg
"""

import os.path
import sys
from pathlib import Path
import glob
import json

# ---------------------------------------------------------------------------
# Import the o2x5xx library.
# When the package is installed the top-level imports are
# used.  When running the script directly from the repository the source folder
# is added to sys.path so the local source code is used instead.
# ---------------------------------------------------------------------------
try:
    from o2x5xx import O2x5xxRPCDevice
    from o2x5xx import O2x5xxPCICDevice
    if not hasattr(sys.modules[__name__], "Simulation"):
        raise ModuleNotFoundError
except (ModuleNotFoundError, ImportError):
    sys.path.append(str(Path(__file__).resolve().parents[2]))
    from source.rpc.client import O2x5xxRPCDevice
    from source.pcic.client import O2x5xxPCICDevice


def check_or_make_directory(path) -> None:
    """Create *path* (including any missing parent directories) if it does not exist yet."""
    if not os.path.exists(path):
        os.makedirs(path)


def generate_dataset_from_ftp_push(ftp_folder_path, read_res_files=True) -> dict:
    """Scan *ftp_folder_path* for JPEG images and group them into batches.

    The sensor's FTP-push feature saves one JPEG file per image per trigger
    cycle.  All images that belong to the same trigger cycle share the same
    timestamp, sensor name, and application name – they are grouped together
    as a *batch*.

    Parameters
    ----------
    ftp_folder_path : str
        Path to the local folder that contains the JPEG files pushed by the
        sensor.
    read_res_files : bool, optional
        If True, reads and includes .res files for each batch. Default is True.

    Returns
    -------
    dict
        A dictionary whose keys are unique batch identifiers of the form
        ``"<timestamp>_<SensorName>_<ApplicationName>"`` and whose values are
        dictionaries with the following keys:

        * ``"timestamp"`` – recording timestamp encoded in the filename
          (e.g. ``"20000101_002456_106"``).
        * ``"sensor_name"`` – name of the sensor that captured the images.
        * ``"application_name"`` – name of the active application at capture
          time.
        * ``"images"`` – list of dicts, each containing ``"image"`` (full file
          path) and ``"image_number"`` (index within the batch, e.g. ``"01"``).
        * ``"batch_pass_fail_result"`` – expected result encoded in the
          filename (``"PASS"`` or ``"FAIL"``).
        * ``"res_data"`` – result data loaded from the corresponding .res file.
    """
    # Collect all JPEG files in the given folder.
    all_jpg_images = glob.glob(r"{folder}\*.jpg".format(folder=ftp_folder_path))
    dataset = {}

    for image in all_jpg_images:
        # Extract metadata that the sensor encoded in the filename.
        filename = os.path.basename(image)
        batch_timestamp = filename.split("_")[0] + "_" + filename.split("_")[1] + "_" + filename.split("_")[2]  # e.g. 20000101_002456_106
        batch_sensor_name = filename.split("_")[3]       # e.g. "Demo Sensor"
        batch_application_name = filename.split("_")[4]  # e.g. "Advanced application"
        batch_image_number = filename.split("_")[5]      # e.g. "01", "02", …
        batch_pass_fail_result = filename.split("_")[6].split(".")[0]  # e.g. "PASS" or "FAIL"

        # Build the unique key that groups images belonging to the same trigger cycle.
        batch_identifier = batch_timestamp + "_" + batch_sensor_name + "_" + batch_application_name

        # Check if a res file for the filename exists - if not skip reading the res file and image.
        # The res file looks like following: 20000101_002448_150_Demo Sensor_Advanced application_PASS.res
        # Compared to an image file: 20000101_002448_150_Demo Sensor_Advanced application_01_PASS.jpg
        res_filename = "_".join(filename.split("_")[:-2]) + "_" + batch_pass_fail_result + ".res"
        res_file = os.path.join(ftp_folder_path, res_filename)

        if read_res_files:
            if not os.path.isfile(res_file):
                print("WARNING: Missing .res file for image {}, skipping this image.".format(image))
                continue
            else:
                with open(res_file, "r") as f:
                    res_data = json.load(f)


        # Create the batch entry the first time this identifier is encountered.
        if batch_identifier not in dataset:
            dataset[batch_identifier] = {
                "timestamp": batch_timestamp,
                "sensor_name": batch_sensor_name,
                "application_name": batch_application_name,
                "images": [],
                "batch_pass_fail_result": batch_pass_fail_result,
                "res_data": res_data
            }

        # Append this image to the batch so we can later replay the whole sequence.
        dataset[batch_identifier]["images"].append({"image": image, "image_number": batch_image_number})

    return dataset


if __name__ == "__main__":

    # ---------------------------------------------------------------------------
    # Step 1 – Build the dataset from the FTP folder.
    # ---------------------------------------------------------------------------
    FTP_FOLDER_PATH = r"C:\ftp\test\FTPUser"  # Enter your FTP folder path here (the folder that contains the JPEG files pushed by the sensor).
    SENSOR_IP_ADDRESS = "192.168.0.69"  # Enter your sensor's IP address here. Make sure to use the correct IP address if you have multiple sensors in your network.
    SENSOR_PORT = 50010  # Enter the PCIC port configured on your sensor for outputting results (default is 50010).
    my_dataset = generate_dataset_from_ftp_push(ftp_folder_path=FTP_FOLDER_PATH)

    # Print total number of batches found in the dataset.
    print("Total number of batches in dataset: {}".format(len(my_dataset)))

    # ---------------------------------------------------------------------------
    # Step 2 – Connect to the sensor and replay each batch in simulation mode.
    # ---------------------------------------------------------------------------
    # Open a PCIC connection (port 50010) to receive application results and an
    # RPC connection (port 80) to control the sensor configuration.
    with O2x5xxPCICDevice(address=SENSOR_IP_ADDRESS, port=SENSOR_PORT) as pcic_device:
        with O2x5xxRPCDevice(address=SENSOR_IP_ADDRESS) as rpc:
            # Request an exclusive session so we can change the operating mode.
            with rpc.mainProxy.requestSession():
                # Switch to operating mode 2 (simulation mode) – this allows
                # sending arbitrary image sequences to the sensor's vision pipeline
                # instead of relying on the live camera image.
                with rpc.sessionProxy.setOperatingMode(mode=2):
                    # Obtain the simulation proxy that provides the FTP-replay API.
                    simulation = rpc.simulation

                    for batch_number, (batch_identifier, batch_data) in enumerate(my_dataset.items(), start=1):
                        # Sort the images by their index so they are fed into the
                        # pipeline in the correct order (01, 02, 03, …).
                        image_paths_ordered = [
                            image_info["image"]
                            for image_info in sorted(batch_data["images"], key=lambda x: x["image_number"])
                        ]

                        # Build the binary payload list expected by the simulation API.
                        payloadList = simulation.createPayloadList(image_paths_ordered)

                        # Send the image sequence to the sensor and trigger processing.
                        # force_trigger=True ensures the pipeline runs even if no
                        # external trigger signal is present.
                        simulation.processImageSequence(image_sequence=payloadList, force_trigger=True)

                        # Read the application result returned by the sensor via PCIC.
                        # The sensor is configured to output results in the format:
                        #   "<BatchIdentifier>;<Result>"
                        # where <Result> is "1" for PASS and "0" for FAIL.
                        ticket, answer = pcic_device.read_next_answer()

                        # TODO: Enter your index here for your own PASS/FAIL result from the PCIC interface.
                        application_result = answer.decode().split(";")[1].strip()  # raw value: "1" or "0"

                        # Convert the numeric result to a human-readable label.
                        application_result = "PASS" if application_result == "1" else "FAIL" if application_result == "0" else application_result

                        print("Processed batch {} of {}: {} with result: {}".format(
                            batch_number, len(my_dataset), batch_identifier, answer.decode()
                        ))

                        # Verify that the result matches the PASS/FAIL label that was
                        # encoded in the original filename.  A mismatch indicates that
                        # the sensor's detection logic produced a different outcome when
                        # replaying the image compared to the live capture.
                        if application_result != batch_data["batch_pass_fail_result"]:
                            print("WARNING: Result mismatch for batch {}: expected {}, got {}".format(
                                batch_identifier, batch_data["batch_pass_fail_result"], application_result
                            ))
