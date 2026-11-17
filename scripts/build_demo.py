from pathlib import Path
import shutil
for name in ['tracks.json','evaluation.json','evaluation_users.json']:shutil.copy2(Path('data/soundmatch')/name,Path('docs')/name)
