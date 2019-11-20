# Open Data Hub Alexa Skill

This repository provides the main components to build a functiong Alexa voice skill (in this case the ODH Voice skill). This is not an Alexa skill template and cannot be directly cloned and used to create a new skill via the CLI, since the original skill was created as a self-hosted one.


## Project Information

In the repository root we can distinguish the two main components that make up an Alexa Skill:

1. models

    The models folder contains inside a .json file named after the locale specification. This file is the interaction model of our skill, basically where we define the skill logic and also the VI (voice interface). You can edit the .json file to make changes to the model but we highly suggest using the Alexa developer console and loading the file there so that you can rely on the GUI, it makes the process much simpler. More on skill models can be found [here](https://developer.amazon.com/docs/custom-skills/create-the-interaction-model-for-your-skill.html) and [here](https://developer.amazon.com/docs/devconsole/create-a-skill-and-choose-the-interaction-model.html).

2. lambda

    This directory contains the code which handles how Alexa responds to intents defined in the interaction model explained above. You can see that there are four files inside:
    - data.py:

         Contains static variables and the queries that the main code file (lambda_function.py) will use

    - lambda_function.py:

         This is the "main code file" that will contain all the functions which will dictate how Alexa responds and also how we handle user intent. Inside this file you are essentially deciding how your skill will operate. It is the most important part of skill development along with the interaction model so read more about the actual technology [here](https://developer.amazon.com/docs/custom-skills/host-a-custom-skill-as-an-aws-lambda-function.html) and more about the actual coding by following [this Amazon tutorial](https://developer.amazon.com/en-US/alexa/alexa-skills-kit/resources/training-resources/cake-walk/cake-walk-1)

    - utils.py:

         This file is created when you initially create the skill in the Alexa developer console as a Python project and it is basically needed to generate a presigned URL to share an S3 object (which is where you can persist memory changes for Alexa hosted skills). You can see how your Alexa hosted S3 bucket can help the skill [here](https://developer.amazon.com/en-US/alexa/alexa-skills-kit/resources/training-resources/cake-walk/cake-walk-5)

    - requirements.txt:

         Contains all the external python modules we want to install for the skill to run. All of the module installation is handled by Lambda so all we do here is just specify the module names. If you have worked with Python before then you will be quite familiar with this file.


    ## Amazon ASK CLI
    This project was downloaded from the Alexa development console using the ASK CLI from amazon. To understand how to use it in regard to a skill and how it helps development and testing you can check [here](https://developer.amazon.com/docs/hosted-skills/build-a-skill-end-to-end-using-an-alexa-hosted-skill.html#askcli).
    We highly reccomend reading through all the links provided here since the Alexa skill building workflow is not "the most typical". Hopefully after reading the Amazon tutorials and guides you will have a clearer idea of how the whole process works and be able to contribute or create your own skills. Check out the [ASK CLI Command Reference](https://developer.amazon.com/docs/smapi/ask-cli-command-reference.html) for more info on all the ask commands possible.

    ## Development Ideas
    The first step towards developing a new skill would be to create a new one from the Alexa developer console. We suggest using the console to build and edit the model but after creating the new skill you can either copy paste the code in models/ and lambda/ in the respesctively the Build and Code tabs inside the developer console or use the ask cli to clone the skill on your computer and copy paste the code there. Afterwards you can deploy the skill to the developer console using the cli. If you wish to use the ask cli then your workflow could follow roughly the following pattern:
    1) Initialize the ASK-CLI with your Amazon developer account credentials using `ask init`
    2) Clone the skill you created in the developer console: `ask clone`
    3) Add and commit the changes made in dev and then merge dev to master by using `ask deploy`
    4) Even more flexible: edit the model using the developer console and you can edit the code locally. You can then work on the code on your favourite editor and deploy only the code by using `ask deploy -t lambda`. This way the deployment won't affect the model that is already online. 

    ## Useful links
      - [Alexa: Skill building basics](https://developer.amazon.com/docs/custom-skills/steps-to-build-a-custom-skill.html)
      - [Alexa: Skill building tutorial from scratch](https://developer.amazon.com/en-US/alexa/alexa-skills-kit/resources/training-resources/cake-walk)
      - [Alexa: Skill building from a template](https://developer.amazon.com/docs/custom-skills/create-custom-skill-from-quick-start-template.html)
      - [Alexa: Template for a skill on Github](https://github.com/alexa/skill-sample-python-quiz-game)
      - [ASK CLI Command Reference](https://developer.amazon.com/docs/smapi/ask-cli-command-reference.html)
      - [Python SPARQL](https://rdflib.github.io/sparqlwrapper/)

