# -*- coding: utf-8 -*-

# simple imports
import logging
import requests
import random
import ask_sdk_core.utils as ask_utils

# from imports
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response
from SPARQLWrapper import SPARQLWrapper, JSON

# local imports
import data

# set logging levels, this is used for debugging when testing the skill
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# sparlq endpoint
sparql_endpoint = SPARQLWrapper("https://sparql.opendatahub.testingmachine.eu/sparql")


class LaunchRequestHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        logger.info("Launching skill...") 
        
        speech = random.choice(data.WELCOME)
        speech += " " + data.HELP
        handler_input.response_builder.speak(speech)
        handler_input.response_builder.ask(data.GENERIC_REPROMPT)
        return handler_input.response_builder.response


class LodgingSearchIntentHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("LodgingSearchIntent")(handler_input)

    def handle(self, handler_input):
        # lambda log
        logger.info("In LodgingSearchIntent handle function")
        
        # get slots from user input
        slots = handler_input.request_envelope.request.intent.slots
        
        # open the attribute manager so that we can then save things to the session attributes
        attribute_manager = handler_input.attributes_manager
        session_attr = attribute_manager.session_attributes

        # Init the variables we'll use to parametrize our queries
        city = ""
        nr_lodgings = "" 
        lodging_type = ""
        
        # Get the values from the slots and prepare the parameters to pass to the queries
        user_ltype = str(slots["lodgingType"].value).lower()
        if(user_ltype in "hotels"):
            lodging_type = "Hotel"
        elif(user_ltype in "hostels"):
            lodging_type = "Hostel"
        elif(user_ltype in "campgrounds"):
            lodging_type = "Campground"
        else:
            lodging_type = "BedAndBreakfast"
        
        # Example of loggin that can be useful for debugging
        # logger.info("Gave city value " + city)
        # logger.info(" Gave lodging_type value " + lodging_type)
        final_speech = ""
        query_string = ""
        hotel_name = ""
        
        final_speech += "Ok, so I looked for " + nr_lodgings + " " + user_ltype + " in <lang xml:lang='it-IT'> " + city + "</lang> and "
        query_string = data.Q_RANDOM_LODGING_CITY.format(lodging_type, city, nr_lodgings)
            
        try:
            sparql_endpoint.setQuery(query_string)
            sparql_endpoint.setReturnFormat(JSON)
            results = sparql_endpoint.query().convert()

            # Format the answer for the user
            if (len(results["results"]["bindings"]) == 0):
                final_speech += " I found no results for what you asked, sorry. "
                handler_input.response_builder.speak(final_speech)
                return handler_input.response_builder.response
            elif (len(results["results"]["bindings"]) == 1):
                final_speech += " I found something. "
                for result in results["results"]["bindings"]:
                    hotel_name = str(result["posLabel"]["value"])
                    final_speech += "The " + user_ltype + " is called <lang xml:lang='de-DE'>" + \
                                    str(result["posLabel"]["value"]) + "</lang> and it's located in <lang xml:lang='it-IT'>" \
                                    + str(result["addr"]["value"]) + " " + str(result["loc"]["value"]) + "</lang>. "
            else:
                final_speech += " I found " + str(len(results["results"]["bindings"])) + ". "
                for count, result in enumerate(results["results"]["bindings"]):
                    final_speech += "Hotel number " + str(count + 1) + " is called <lang xml:lang='de-DE'>" + str(
                        result["posLabel"]["value"]) + "</lang> and it's located in <lang xml:lang='it-IT'>" \
                        + str(result["addr"]["value"]) + " " + str(result["loc"]["value"]) + "</lang>. "
        except Exception:
            handler_input.response_builder.speak("There was a problem with the service request. ")
            return handler_input.response_builder.response
        
        session_attr["hotel_name"] = 
        final_speech += "Would you like to know how many stars the hotels has ?"
        handler_input.response_builder.speak(final_speech).ask(final_speech)
        return handler_input.response_builder.response


class WineSearchIntentHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("WineSearchIntent")(handler_input)

    def handle(self, handler_input):
        # lambda log
        logger.info("In WineSearchIntentHandler")
            
        # prepare result statement
        final_speech = ""
        query_string = str(data.Q_WINE)
        
        try:
            sparql_endpoint.setQuery(query_string)
            sparql_endpoint.setReturnFormat(JSON)
            results = sparql_endpoint.query().convert()
            
            # Format the answer for the user
            if (len(results["results"]["bindings"]) == 0):
                final_speech += " I found no results for what you asked, sorry. "
            else:
                for result in results["results"]["bindings"]:
                    final_speech += "I would suggest a bottle of <lang xml:lang='de-DE'>" + str(result["name"]["value"]) + \
                    "</lang>. It tastes great and it also won an award in " + str(result["vintage"]["value"]) + " ."
        except Exception:
            handler_input.response_builder.speak("There was a problem with the service request. ")
            return handler_input.response_builder.response

        handler_input.response_builder.speak(final_speech)
        return handler_input.response_builder.response


class AboutIntentHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AboutIntent")(handler_input)
    
    def handle(self, handler_input):
        # lambda log
        logger.info("In AboutIntentHandler")
        
        speech = data.ABOUT
        speech += " " + data.GENERIC_REPROMPT

        handler_input.response_builder.speak(speech)
        handler_input.response_builder.ask(data.GENERIC_REPROMPT)
        return handler_input.response_builder.response

class ThankIntentHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("ThankIntent")(handler_input)
    
    def handle(self, handler_input):
        # lambda log
        logger.info("In ThankIntentHandler")
        
        speech = random.choice(data.THANK_RESPONSE)

        handler_input.response_builder.speak(speech)
        handler_input.response_builder.ask(data.GENERIC_REPROMPT)
        return handler_input.response_builder.response


class HelpIntentHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = data.HELP

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Bye bye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .set_should_end_session
                .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.
        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """

    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.
sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(LodgingSearchIntentHandler())
sb.add_request_handler(WineSearchIntentHandler())
sb.add_request_handler(ThankIntentHandler())
sb.add_request_handler(AboutIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(
    IntentReflectorHandler())  # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()