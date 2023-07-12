# reliable-credit-scoring-system
Implementation of and end to end credit system scoring system. This starts from data ingestion to a deployment and monitoring with a full CICD with best practices of MLOPS.

## Model Development

This is a stage in which the model is developed. The project here is building a risk scoring system where every customer is assigned a score that will range from 350 to 950. Details of the model are found in the [credit risk model directory](credit-risk-model).

## Monitoring

Models depreciate, data changes, many things can go wrong! Monitoring provide us the ability to understand the behaviour of our system as changes occur. It provide us the ability to possibily metigate down town before they occur. Our system uses [Evidently to monitor](monitoring) the services and display metrics via Gafana.

## Code Quality

Quality and standards helps us metigate drift in out code. It also help us to identify non conforming code as well as vulnerabilities. Standards are maintained via continous testing of out code. This is achieved via [unit test](automation/tests/), [integration test](automation/integration-test). We also use SonarQube to monitor the quality and display it beautifully in a dasboard.

## [Continuous Integration](.github/actions/ci-test.yaml)

To ensure that our development is smooth and free from manual errors, we implented continuous integration to ensure that our components integrates properly. We leverage the power of GitHub Actions to ensure that our system stays intact as we develop new features.

## [Continuous Delivery](.github/actions/cd-deploy.yaml)

To ensure that our model and artifacts are delivered in a timely and consisten fashion, we implented continuous delivery to ensure that our model is continually deployed when ever a feature is added that makes the final cut.
