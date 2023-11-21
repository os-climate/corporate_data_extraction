import os

import requests


def main(app_type, project_name, s3_usage, mode):
    """
    This function either starts a training or an inference run for a specific project by sending a request
    to another server.

    :param app_type: string: application type which is either inference or training
    :param project_name: string
    :param s3_usage: string: either Y or N
    :param mode: string: RB, ML, both, or none - for just doing postprocessing
    :return:
    """
    if app_type not in ["training", "inference"]:
        print("app_type should be training or inference. Please restart with valid input.")
        return False

    if s3_usage not in ["Y", "N"]:
        print("s3_usage should be Y or N. Please restart with valid input.")
        return False

    if mode not in ["RB", "ML", "both", "none"]:
        print("mode should be RB, ML, both or none. Please restart with valid input.")
        return False

    coordinator_ip = os.getenv("coordinator_ip")
    coordinator_port = os.getenv("coordinator_port")

    # Example string http://172.40.103.147:2000/liveness
    liveness_string = f"http://{coordinator_ip}:" f"{coordinator_port}/liveness"
    coordinator_server_live = requests.get(liveness_string)
    if coordinator_server_live.status_code == 200:
        print(f"Coordinator server is up. Proceeding to the task {app_type} with project {project_name}.")
    else:
        print("Coordinator server is not responding.")
        return False

    if app_type == "training":
        print(f"We will contact the server to start training for project {project_name}.")
        # Example string http://172.40.103.147:2000/train?project_name=ABC&s3_usage=Y
        train_string = (
            f"http://{coordinator_ip}:"
            f"{coordinator_port}/train"
            f"?project_name={project_name}"
            f"&s3_usage={s3_usage}"
        )
        coordinator_start_train = requests.get(train_string)
        print(coordinator_start_train.text)
        if coordinator_start_train.status_code == 200:
            return True
        else:
            return False
    else:
        print(f"We will contact the server to start inference for project {project_name}.")
        # Example string http://172.40.103.147:2000/infer?project_name=ABC&s3_usage=Y&mode=both
        infer_string = (
            f"http://{coordinator_ip}:"
            f"{coordinator_port}/infer"
            f"?project_name={project_name}"
            f"&s3_usage={s3_usage}"
            f"&mode={mode}"
        )
        coordinator_start_infer = requests.get(infer_string)
        print(coordinator_start_infer.text)
        if coordinator_start_infer.status_code == 200:
            return True
        else:
            return False


if __name__ == "__main__":
    main("training", os.getenv("test_project"), "Y", "both")
    main("inference", os.getenv("test_project"), "Y", "both")
