from huggingface_hub import HfApi, upload_file

repo_id = "georgiosrizos/spider-monkey-detector-SEResNet"
local_model_path = "C:/Users/George/scp_folder/osa_smw_dataset/ResultsOSA/max-SEResNet20-attention-4/whinny_single/au_pr/model.keras"    # your trained model file

api = HfApi()

# Create a repo (if it doesn't already exist)
api.create_repo(repo_id=repo_id, private=False, exist_ok=True)

# Upload the model file
upload_file(
    path_or_fileobj=local_model_path,
    path_in_repo="spider-monkey-detector-SEResNet.keras",     # name inside the repo
    repo_id=repo_id
)

print(f"✅ Uploaded to https://huggingface.co/{repo_id}")
