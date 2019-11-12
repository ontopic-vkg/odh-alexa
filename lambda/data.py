# -*- coding: utf-8 -*-

SKILL_NAME = "ODH"
WELCOME = ["Welcome to the Open Data Hub!", "Hello and Welcome!", "This is the Open Data Hub speaking!"]
HELP = "Say about to hear more about the open data hub or you just ask me about lodging or wine. Say exit to stop this interaction and quit the skill."
ABOUT = "Open Data Hub is your access point to South Tyrol’s relevant data. The data is updated on a regular basis and easily accessible."
STOP = "Okay, see you next time!"
FALLBACK = "Hmmm I can't help you with that. I can help you learn about the open data hub or discover hotels though. Wanna try?"
THANK_RESPONSE = ["No worries.", "I'm here to help", "Glad I could help."]
GENERIC_REPROMPT = "What can I help you with?"

# SPARQL QUERIES
Q_RANDOM_LODGING_CITY = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX schema: <http://schema.org/>

SELECT ?posLabel ?addr ?loc WHERE {{ 
  ?h a schema:{} ; schema:name ?posLabel ; schema:address ?a .
  ?a schema:streetAddress ?addr ; schema:addressLocality ?loc
  FILTER (lang(?posLabel) = 'de' && lang(?addr) = 'it' && lcase(?loc) = lcase('{}'@it)) .
  BIND(RAND() AS ?rand) .
  FILTER(?rand < 0.10) .
}} LIMIT 1"""

Q_LODGING_INFO = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX schema: <http://schema.org/>

SELECT ?posLabel ?addr ?loc WHERE {{ 
  ?h a schema:{} ; schema:name ?posLabel ; schema:address ?a .
  ?a schema:streetAddress ?addr ; schema:addressLocality ?loc
  FILTER (?posLabel = "{}"@de) .
  FILTER (lang(?posLabel) = 'de' && lang(?addr) = 'it') .
  BIND(RAND() AS ?rand) .
  FILTER(?rand < 0.10) .
}} LIMIT 1"""

Q_WINE = """PREFIX : <http://noi.example.org/ontology/odh#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX schema: <http://schema.org/>

SELECT ?name ?vintage ?rand WHERE {
  ?wine a :Wine ; :wineVintageYear ?vintage ; rdfs:label ?name ; :receivesWineAward ?aw.
  BIND(RAND() AS ?rand) .
  FILTER(?rand <= 0.10) .
} LIMIT 1
"""