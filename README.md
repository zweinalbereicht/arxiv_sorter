# arxiv_sorter
## Automatic sorter for arXiv's daily thread.

This script makes a call to the 'cond-mat.stat-mech' arxiv api, retrieves latest unread articles and performs a selection based on the **sorter.toml** file:
```toml
# just add the keywords in this file
[selection]
authors = [
    "parisi",
    "einstein",
]
titles = [
    "glass",
    "loop",
]
```
The results are then sent back to the user's email adress of choice, via the **sendgrid** free service. Email params are passed in the **email_adress.txt** file:
```txt
sengrid_sender_adress@example.com
recipient_adress@example.com
```
### Enjoy 🔭
