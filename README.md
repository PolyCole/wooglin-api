<p>
  <img src="https://i.imgur.com/ssAWf0r.jpg" width="800"></img>
</p>

![CircleCI](https://img.shields.io/circleci/build/github/WooglinAlphaZeta/wooglin-api/main?style=for-the-badge)
<img alt="GitHub last commit" src="https://img.shields.io/github/last-commit/WooglinAlphaZeta/wooglin-api?color=%20%23ff751a&style=for-the-badge">
<img alt="GitHub commit activity" src="https://img.shields.io/github/commit-activity/m/WooglinAlphaZeta/wooglin-api?style=for-the-badge">
***

### Introduction
This repository houses the REST API that allows access to the chapter's data. The API acts as the sole source of truth for data, and will be the backbone of both the SlackBot portion of Wooglin and the eventual SPA portion of Wooglin being privy to the same information. 

### How It Works
The API is written in Python, using Django and the Django Rest Framework. The app is deployed using Heroku and CI/CD is facilitated by CircleCI. The API is documented using Swagger, and the documentation can be found [here](https://wooglin-api.herokuapp.com/api/v1/swagger).
