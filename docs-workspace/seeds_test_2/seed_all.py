# Source extraite de: mission seeds_test_2
# Date: 2026-07-02
# Auteur: CTO kit
#
# Usage:
#   python manage.py shell < ../docs-workspace/seeds_test_2/seed_all.py

import os

BASE = os.path.dirname(os.path.abspath(__file__))

for script in ["seed_superadmin.py", "seed_accounts_test_2.py", "seed_prompts_mk1.py"]:
    path = os.path.join(BASE, script)
    print(f"\n{'=' * 50}\nExecution : {script}\n{'=' * 50}")
    exec(open(path, encoding="utf-8").read())

print("\nKit seeds_test_2 completement rejoue.")
