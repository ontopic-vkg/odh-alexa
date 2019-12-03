# -*- coding: utf-8 -*-

# simple imports
import logging
import requests
import random
import ask_sdk_core.utils as ask_utils

# from imports
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler, AbstractExceptionHandler, AbstractResponseInterceptor, AbstractRequestInterceptor
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import ui, Response
from ask_sdk_model.ui import SimpleCard
from SPARQLWrapper import SPARQLWrapper, JSON
from ask_sdk_core.utils import is_intent_name, is_request_type
from ask_sdk_model.interfaces.display import ImageInstance, Image, RenderTemplateDirective, ListTemplate1, BackButtonBehavior, ListItem, BodyTemplate2, BodyTemplate1
from ask_sdk_core.response_helper import get_plain_text_content, get_rich_text_content
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
        logger.info("Improvement log: Launched open data hub skill")
        
        speech = random.choice(data.WELCOME)
        speech += " " + data.HELP
        handler_input.response_builder.speak(speech)
        handler_input.response_builder.ask(random.choice(data.GENERIC_REPROMPT))
        return handler_input.response_builder.response


class LodgingSearchIntentHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("LodgingSearchIntent")(handler_input)

    def handle(self, handler_input):
        # log intent that was called for insight
        logger.info("Improvement log: User called LodgingSearchIntent")
        
        # get slots from user input
        slots = handler_input.request_envelope.request.intent.slots
        
        # open the attribute manager so that we can then save things to the session attributes
        attribute_manager = handler_input.attributes_manager
        session_attr = attribute_manager.session_attributes

        # Init the variables we'll use to parametrize our queries
        city = ""
        lodging_type = ""
        
        # Get the values from the slots and prepare the parameters to pass to the queries
        city = str(slots["city"].value)
        user_ltype = str(slots["lodgingType"].value).lower()
        if(user_ltype in "hotels"):
            lodging_type = "Hotel"
        elif(user_ltype in "hostels"):
            lodging_type = "Hostel"
        elif(user_ltype in "campgrounds"):
            lodging_type = "Campground"
        else:
            lodging_type = "BedAndBreakfast"
        
        # log the slots the user gave for insight
        logger.info("Improvement log: User requested lodging in " + city)
        logger.info("Improvement log: User requested to lodge in a " + lodging_type)
        
        # add parameters to the query and run it on the VKG
        total_lodgings_query_string = data.Q_NR_LODGINGS_IN_CITY.format(lodging_type, city)
        lodging_query_string = data.Q_RANDOM_LODGING_CITY.format(lodging_type, city)
        total_lodgings_results = query_vkg(total_lodgings_query_string)
        lodging_results = query_vkg(lodging_query_string)

        final_speech = ""
        lodging_name = ""
        
        # Format the final answer speech for the user
        final_speech += "Ok, so I looked for " + user_ltype + " in <lang xml:lang='it-IT'> " + city + "</lang> and "
        lodging_tuples = []
        
        for nr_lodgings in total_lodgings_results["results"]["bindings"]:
            if (nr_lodgings["nrLodgings"]["value"] == 0):
                final_speech += " I found no results for what you asked, sorry. "
                handler_input.response_builder.speak(final_speech)
                return handler_input.response_builder.response
            else:
                final_speech += " I found " + nr_lodgings["nrLodgings"]["value"] + " in total. Here are some suggestions: "
                for count, result in enumerate(lodging_results["results"]["bindings"]):
                    lodging_name = str(result["posLabel"]["value"])
                    lodging_address = str(result["addr"]["value"]) + " " + str(result["loc"]["value"])
                    lodging_phone = str(result["phone"]["value"])
                    final_speech += "Number " + str(count+1) +  " is called <lang xml:lang='de-DE'>" + lodging_name + "</lang>. "
                    lodging_tuples.append((count+1, lodging_name, lodging_address, lodging_phone))
            
        session_attr["lodgings_detail_list"] = lodging_tuples

        final_speech += "I can also provide you with the address and phone number of one the " + user_ltype + " I mentioned before, \
        just tell me which number you are interested in."
        
        handler_input.response_builder.speak(final_speech).ask(final_speech)
        return handler_input.response_builder.response


class GetMoreInfoForNumberHandler(AbstractRequestHandler):
    """Handler for yes to get more info intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        #session_attr = handler_input.attributes_manager.session_attributes
        #return (is_intent_name("GetMoreInfoForNumber")(handler_input) and lodgings_detail_list in )
        logger.info("inside get more info can handle function")
        return ask_utils.is_intent_name("GetMoreInfoForNumber")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("Improvement log: User request to get more info after initial search")
        
        attribute_manager = handler_input.attributes_manager
        session_attr = attribute_manager.session_attributes
        slots = handler_input.request_envelope.request.intent.slots
        
        if(session_attr["lodgings_detail_list"] is None and session_attr["foode_detail_list"] is None):
            handler_input.response_builder.speak("I don't know how to help you with that, sorry!")
            return handler_input.response_builder.response
        elif("lodgings_detail_list" in session_attr):
            user_lodging_nr = slots["info_number"].value
            lodgings_detail_list = session_attr["lodgings_detail_list"]
            lodging_details = lodgings_detail_list[int(user_lodging_nr)-1]
            name = lodging_details[1]
            address = lodging_details[2]
            phone_nr = lodging_details[3]
        elif("foode_detail_list" in session_attr):
            user_foode_nr = slots["info_number"].value
            foode_detail_list = session_attr["lodgings_detail_list"]
            foode_details = foode_detail_list[int(user_foode_nr)-1]
            name = foode_details[1]
            address = foode_details[2]
            phone_nr = foode_details[3]
        
        logger.info("Improvement log: User asked for more info on " + name)

        # Format the final answer speech for the user
        final_speech = ""
        phone_nr = ""

        if (len(lodgings_detail_list) < int(user_lodging_nr)):
            final_speech += "I don't have any info on that because I didn't mention that number. \
            Please try with one of the numbers I mentioned before"
            handler_input.response_builder.speak(final_speech)
            return handler_input.response_builder.response
        else:
            final_speech += "The address of <lang xml:lang='de-DE'> " + name + "</lang> is <lang xml:lang='it-IT'>" \
            + address + "</lang>. Their phone number is " + phone_nr + " . "

        card_info = "{}, {}.\nPhone number: {}\n".format(name, address, phone_nr)

        if (dev_supports_display(handler_input)):
            primary_text = get_rich_text_content(card_info)
            final_speech += "Looks like you have a display, you can also check the details I just mentioned there. \
            Have a good time and see you later."

            handler_input.response_builder.add_directive(
                RenderTemplateDirective(BodyTemplate1(title=data.SKILL_NAME, text_content=primary_text))
                )
        else:
            final_speech += "I'm sending you this info also on the Alexa app so you can check it there. Have a good time and see you later."
            handler_input.response_builder.set_card(SimpleCard(title=data.SKILL_NAME, content=card_info))
        
        logger.info("Improvement log: User got all the extra info for the lodging search")
        
        handler_input.response_builder.speak(final_speech)
        session_attr["lodgings_detail_list"] = None
        return handler_input.response_builder.response


class NoMoreLodgingInfoIntentHandler(AbstractRequestHandler):
    """Handler for no to get no more info intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        session_attr = handler_input.attributes_manager.session_attributes
        return (is_intent_name("AMAZON.NoIntent")(handler_input) and "lodgings_detail_list" in session_attr)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("Improvement log: User didn't want any more information after launching the lodging search")

        final_speech = "Ok then, hope I was helpful."
        handler_input.response_builder.speak(final_speech)
        session_attr["lodgings_detail_list"] = None
        return handler_input.response_builder.response


class FoodSearchIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("FoodSearchIntent")(handler_input)

    def handle(self, handler_input):
        # log intent that was called for insight
        logger.info("Improvement log: User called FoodSearchIntent")
        
        slots = handler_input.request_envelope.request.intent.slots
        attribute_manager = handler_input.attributes_manager
        session_attr = attribute_manager.session_attributes

        city = ""
        foode_type = ""
        
        # Get the values from the slots and prepare the parameters to pass to the queries
        city = str(slots["city"].value)
        user_ftype = str(slots["establishmentType"].value).lower()
        if(user_ftype in "restaurants"):
            foode_type = "Restaurant"
        elif(user_ftype in "bars" or user_ftype in "pubs"):
            foode_type = "BarOrPub"
        else:
            foode_type = "FastFoodRestaurant"
        
        # log the slots the user gave for insight
        logger.info("Improvement log: User requested to eat in " + city)
        logger.info("Improvement log: User requested to eat in a " + foode_type)
        
        # add parameters to the query and run it on the VKG
        total_foode_query_string = data.Q_NR_FOODE_IN_CITY.format(foode_type, city)
        foode_query_string = data.Q_RANDOM_FOODE_CITY.format(foode_type, city)
        total_foode_results = query_vkg(total_foode_query_string)
        foode_results = query_vkg(foode_query_string)

        final_speech = ""
        foode_name = ""
        
        # Format the final answer speech for the user
        final_speech += "Ok, so I looked for " + user_ftype + " in <lang xml:lang='it-IT'> " + city + "</lang> and "
        foode_tuples = []
        
        for nr_foode in total_foode_results["results"]["bindings"]:
            if (nr_foode["nrEstablishments"]["value"] == 0):
                final_speech += " I found no results for what you asked, sorry. "
                handler_input.response_builder.speak(final_speech)
                return handler_input.response_builder.response
            else:
                final_speech += " I found " + nr_foode["nrEstablishments"]["value"] + " in total. Here are some suggestions: "
                for count, result in enumerate(foode_results["results"]["bindings"]):
                    foode_name = str(result["posLabel"]["value"])
                    foode_address = str(result["addr"]["value"]) + " " + str(result["loc"]["value"])
                    foode_phone = str(result["phone"]["value"])
                    final_speech += "Number " + str(count+1) +  " is called <lang xml:lang='de-DE'>" + foode_name + "</lang>. "
                    foode_tuples.append((count+1, foode_name, foode_address, foode_phone))
            
        session_attr["foode_detail_list"] = foode_tuples

        final_speech += "I can also provide you with the address and phone number of one the " + user_ftype + " I mentioned before, \
        just tell me which number you are interested in."
        
        handler_input.response_builder.speak(final_speech).ask(final_speech)
        return handler_input.response_builder.response


class NoMoreFoodInfoIntentHandler(AbstractRequestHandler):
    """Handler for no to get no more info intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        session_attr = handler_input.attributes_manager.session_attributes
        return (is_intent_name("AMAZON.NoIntent")(handler_input) and "foode_detail_list" in session_attr)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("Improvement log: User didn't want any more information after launching the food eastablishment search")

        final_speech = "Ok then, hope I was helpful."
        handler_input.response_builder.speak(final_speech)
        session_attr["foode_detail_list"] = None
        return handler_input.response_builder.response


class WineSearchIntentHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("WineSearchIntent")(handler_input)

    def handle(self, handler_input):
        # lambda log
        logger.info("Improvement log: User called WineSearchIntent")
        
        attribute_manager = handler_input.attributes_manager
        session_attr = attribute_manager.session_attributes
        
        query_string = str(data.Q_WINE)
        results = query_vkg(query_string)
            
        # prepare result statement
        final_speech = ""
        wine_name = ""
            
        # Format the answer for the user
        if (len(results["results"]["bindings"]) == 0):
            final_speech += " I found no results for what you asked, sorry. "
        else:
            for result in results["results"]["bindings"]:
                wine_name = str(result["name"]["value"])
                wine_award_name = str(result["aw"]["value"])
                final_speech += "I would suggest a bottle of <lang xml:lang='de-DE'>" + str(result["name"]["value"]) + \
                "</lang>. It tastes great and it also won an award in " + str(result["vintage"]["value"]) + " ."
        
        wine_and_award = (wine_name, wine_award_name)
        session_attr["wine_and_award"] = wine_and_award
        handler_input.response_builder.speak(final_speech)
        return handler_input.response_builder.response


class GetWineAwardNameIntentHandler(AbstractRequestHandler):
    """Handler for yes to get more info intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        session_attr = handler_input.attributes_manager.session_attributes
        return (is_intent_name("GetWineAwardNameIntent")(handler_input) and "wine_and_award" in session_attr)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("Improvement log: User looked to get some information on the award")
        
        attribute_manager = handler_input.attributes_manager
        session_attr = attribute_manager.session_attributes

        wine_and_award = session_attr["wine_and_award"]
        
        logger.info("Improvement log: User asked for the award of the wine called " + wine_and_award[0])

        # Format the final answer speech for the user
        final_speech = "The award that <lang xml:lang='de-DE'>" + wine_and_award[0] + "</lang> won was the " + \
        wine_and_award[1] + " award. Pretty cool huh."
        
        session_attr["wine_and_award"] = None
        
        handler_input.response_builder.speak(final_speech)
        return handler_input.response_builder.response

class CustomFallbackIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("CustomFallbackIntent")(handler_input)
        
    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        user_query = str(slots["userQuery"].value)
        
        logger.info("Improvement log: Skill did not understand the user query. Now asking user if we can register it.")

        attribute_manager = handler_input.attributes_manager
        session_attr = attribute_manager.session_attributes
        session_attr["log_user_query"] = user_query
        
        final_speech = "I didn't quite get that. Can I record the question in order to improve myself and this service?"
        handler_input.response_builder.speak(final_speech).ask(final_speech)
        return handler_input.response_builder.response

class YesForQueryLogIntentHandler(AbstractRequestHandler):
    """Handler for yes to get more info intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        session_attr = handler_input.attributes_manager.session_attributes
        return (is_intent_name("AMAZON.YesIntent")(handler_input) and "log_user_query" in session_attr)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        attribute_manager = handler_input.attributes_manager
        session_attr = attribute_manager.session_attributes

        log_user_query = session_attr["log_user_query"]
        logger.info("Improvement: ODH did not understand the following user query: " + log_user_query)

        final_speech = "Thank you very much for your cooperation. Have a good time and see you later."

        handler_input.response_builder.speak(final_speech).set_should_end_session(True)
        return handler_input.response_builder.response


class NoForQueryLogIntentHandler(AbstractRequestHandler):
    """Handler for no to get no more info intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        session_attr = handler_input.attributes_manager.session_attributes
        return (is_intent_name("AMAZON.NoIntent")(handler_input) and "log_user_query" in session_attr)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("Improvement log: User did not allow us to register his query.")

        final_speech = "Ok then, I won't use what you asked me to further improve. Thanks and bye!"
        handler_input.response_builder.speak(final_speech).set_should_end_session(True)
        return handler_input.response_builder.response


class AboutIntentHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AboutIntent")(handler_input)
    
    def handle(self, handler_input):
        logger.info("Improvement log: User called AboutIntent")
        
        speech = data.ABOUT

        handler_input.response_builder.speak(speech)
        handler_input.response_builder.ask(random.choice(data.GENERIC_REPROMPT))
        return handler_input.response_builder.response

class ThankIntentHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("ThankIntent")(handler_input)
    
    def handle(self, handler_input):
        logger.info("Improvement log: User called ThankIntent")
        
        speech = random.choice(data.THANK_RESPONSE)

        handler_input.response_builder.speak(speech).set_should_end_session(False)
        return handler_input.response_builder.response


class HelpIntentHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("Improvement log: User called HelpIntent")
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
        logger.info("Improvement log: User called CancelIntent or StopIntent")
        speak_output = "Bye bye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .set_should_end_session(True)
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
        logger.info("Improvement log: Something happened which triggered an exception. More information below:")
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# Auxilliary functions that can be used in more than one handler

# Performs the queries we want on the VKG
def query_vkg(query_string):
    try:
        sparql_endpoint.setQuery(query_string)
        sparql_endpoint.setReturnFormat(JSON)
        results = sparql_endpoint.query().convert()
        return results
    except Exception:
        raise Exception("There was a problem with the service request.")

# Check if the current device has a screen display
def dev_supports_display(handler_input):
    # type: (HandlerInput) -> bool
    """Check if display is supported by the skill."""
    try:
        if hasattr(
                handler_input.request_envelope.context.system.device.
                        supported_interfaces, 'display'):
            return (
                    handler_input.request_envelope.context.system.device.
                    supported_interfaces.display is not None)
    except:
        return False


# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.
sb = SkillBuilder()

# First skill to process is of course the launch request
sb.add_request_handler(LaunchRequestHandler())
# Lodging logic handlers -----------------------------------
sb.add_request_handler(LodgingSearchIntentHandler())
sb.add_request_handler(NoMoreLodgingInfoIntentHandler())
# ----------------------------------------------------------
# Food establishments logic handlers ------------------------
sb.add_request_handler(FoodSearchIntentHandler())
sb.add_request_handler(NoMoreFoodInfoIntentHandler())
# ----------------------------------------------------------
# The handler for "more information on number x"
sb.add_request_handler(GetMoreInfoForNumberHandler())
# ----------------------------------------------------------
# Wine logic handlers -----------------------------------
sb.add_request_handler(WineSearchIntentHandler())
sb.add_request_handler(GetWineAwardNameIntentHandler())
# ----------------------------------------------------------
# Custom Fallback: Log user questions ----------------------
sb.add_request_handler(CustomFallbackIntentHandler())
sb.add_request_handler(YesForQueryLogIntentHandler())
sb.add_request_handler(NoForQueryLogIntentHandler())
# ----------------------------------------------------------
# Classic interaction handlers -----------------------------
sb.add_request_handler(ThankIntentHandler())
sb.add_request_handler(AboutIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler())  # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers
# Exception handler ----------------------------------------
sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()