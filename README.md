# QuestionContest
Friendly contest for completing practice questions to encourage students to study for exams. Users register individual accounts then self score themselves on how many questions they have completed. A leaderboard displays the highest scorers.

## SQL Setup Commands
```
CREATE TABLE accounts (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, username TEXT NOT NULL, hash TEXT NOT NULL, questions INTEGER NOT NULL);
```
