import yaml
import requests


def main(app_type, project_name, s3_usage, mode):
    """
    This function either starts a training or an inference run for a specific project.

    :param app_type: string: application type which is either inference or training
    :param project_name: string
    :param s3_usage: string: either Y or N
    :param mode: string: RB, ML, both, or none - for just doing postprocessing
    :return:
    """

    f = open('/coordinator_settings.yaml', 'r')
    coordinator_settings = yaml.safe_load(f)
    f.close()
    coordinator_server_live = requests.get(f"http://{coordinator_settings['coordinator_ip']}:" +
                                           f"{coordinator_settings['coordinator_port']}/liveness")
    if coordinator_server_live.status_code == 200:
        print(f"Coordinator server is up. Proceeding to the task {app_type} with project {project_name}.")
    else:
        print("Coordinator server is not responding.")
        return False
