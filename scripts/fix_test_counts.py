import sqlite3
from pathlib import Path
DB = Path(__file__).resolve().parent.parent / 'results' / 'results.db'
conn = sqlite3.connect(str(DB))
conn.execute("UPDATE experiment_results SET tests_passed_before=405, tests_total_before=602 WHERE condition='K' AND repo='requests'")
conn.execute("UPDATE experiment_results SET tests_passed_before=1003, tests_total_before=1024 WHERE condition='K' AND repo='httpie'")
conn.commit()
for row in conn.execute(
        "SELECT repo, tests_passed_before, tests_total_before FROM experiment_results WHERE condition='K' GROUP BY repo"):
    print(f'{row[0]}: passed={row[1]}, total={row[2]}')
conn.close()
print('Done')
