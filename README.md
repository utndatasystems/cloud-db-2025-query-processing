1. Python dependencies: `pip install -r requirements.txt`
1. Copy the downloaded dataset into the root directory of the repo.
1. Create a copy of the template (`group-template`), please prefix your group folder with `group-`:
   ```bash
   cp -rf group-template group-awesome
   ```
1. Run your solution:
   ```bash
   python3 group-awesome/aggregation.py
   ```
1. Run all solutions:

   aggregation
   ```bash
   python leaderboard.py aggregation group-*
   ```
   join
   ```bash
   python leaderboard.py join group-*
   ```
1. Checkin:
   ```bash
   git add group-aweseome
   git commit -m "updated group-awesome"
   git fetch && git rebase origin/main && git push origin main
   ```