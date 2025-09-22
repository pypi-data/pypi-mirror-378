# from pathlib import Path
# def load_single_cte_system_prompt() -> str:
#  here = Path(__file__).resolve().parents[1]
#  prompt_path = '/Workspace/Users/yashraj.singh1@chubb.com/.bundle/agentic_data_annotations/dev/files/prompts/single_cte_system.md'
#  return prompt_path.read_text(encoding="utf-8")


from pathlib import Path

def load_single_cte_system_prompt() -> str:
 # base_dir = Path(file).resolve().parents[1]
 # points to the 'files' directory
 prompt_path = ( Path("/Workspace") / "Users" / "yashraj.singh1@chubb.com" / ".bundle" / "agentic_data_annotations" / "dev" / "files" / "prompts" / "single_cte_system.md" )
 return prompt_path.read_text(encoding="utf-8")