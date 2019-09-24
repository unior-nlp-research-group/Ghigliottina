import utility

BUTTON_INFO = 'ℹ️ INFO'
BUTTON_SOLVER = '🔍 RISOLUTORE'
BUTTON_GENERATOR = '🧩 GENERATORE'
BUTTON_ADMIN = "🔑 Admin"
BUTTON_BACK = "🔙 INDIETRO"
BUTTON_SOLUTION = "🔐 SOLUZIONE"

BUTTON_YES = '👌 SI'
BUTTON_NO = '🙅‍♀️ NO'


MSG_INTRO = (
    "🤠 Ciao, sono un bot in grado di risolvere o generare "
    "Ghigliottine del gioco dell'Eredità di Rai1.\n\n"
    "Premi su {} se vuoi mandarmi una Ghigliottina da risolvere "
    "oppure {} se vuoi che te ne dia io una da risolvere."
).format(BUTTON_SOLVER, BUTTON_GENERATOR)

MSG_SOLVER_INTRO = (
    "🧐 Prova a mettermi alla prova scrivendo 5 indizi "
    "separati da spazi o da virgole, ad esempio scrivi\n\n"
    "*oro argento previsione colazione punta*\n\n"
    "(oppure mandami un'immagine della TV con i 5 indizi)."
)

MSG_INFO = (
    "🤖 Bot sviluppato da Federico Sangati (@kercos) "
    "in collaborazione di UNIOR NLP Research Group dell'Università di Napoli\n"
    "https://sites.google.com/view/unior-nlp-research-group"
)

MSG_GENERATOR_INTRO = "🧩 Trova la parola associata a questi 5 indizi:\n\n*{}*"
MSG_SOLUTION = "🔐 La soluzione della ghigliottina è *{}*."
MSG_GUESS_OK = "✅ Bravissimo/a hai indovinato!"
MSG_GUESS_KO = "❌ Mi dispiace, hai sbagliato. Riprova!"
MSG_EXPLANATIONS = "Queste le spiegazioni:\n{}"
MSG_CONTINUE = "🔁 Vuoi continuare?"

MSG_TOO_EARLY = "⏰ Troppo presto... prova a pensarci ancora un po'."

MSG_SEND_PHOTO_NOT_DOCUMENT = "⛔️ Mandami l'immagine come *Foto* e non come documento."
MSG_WRONG_INPUT_ONLY_TEXT_ACCEPTED = "⛔️ Input non valido, devi inserire solo del testo."
MSG_WRONG_INPUT_USE_TEXT = '⛔ Input non valido, per favore inserisci del testo.'
MSG_WRONG_INPUT_USE_TEXT_OR_BUTTONS = '⛔️ Input non valido, per favore inserisci del testo o usa i pulsanti 🎛'
MSG_WRONG_INPUT_INSRT_NUMBER = '⛔️🔢 Input non valido, per favore inserisci un numero.'
MSG_WRONG_INPUT_INSRT_NUMBER_BETWEEN = '⛔️🔢 Input non valido, per favore inserisci un numero da {} a {}.'
MSG_WRONG_INPUT_USE_BUTTONS = '⛔️ Input non valido, per favore usa i pulsanti 🎛'
MSG_WRONG_INPUT_USE_BUTTONS_TEXT_PHOTO = '⛔️ Input non valido, per favore usa i pulsanti, testo o immagini.'
MSG_WRONG_BUTTON_INPUT = '⛔️ Input non valido, probabilmente hai premuto un tasto due volte.'
MSG_INPUT_TOO_SHORT = '⛔️ Input troppo corto.'
MSG_INPUT_CONTAINS_SPACE_OR_MARKDOWN = '⛔️ Input non può conotenere spazi o i caratteri: "{}".'.format(utility.escape_markdown(utility.MARKDOWN_CHARS))
MSG_INPUT_NO_MARKDOWN = '⛔️ Il testo non può contenere i caratteri: {}'.format(utility.escape_markdown(utility.MARKDOWN_CHARS))
MSG_COMMAND_NOT_RECOGNIZED = '⛔️ Comando non riconosciuto.'


MSG_REFRESH_INTERFACE = "🤖 Il chatbot è stato aggiornato."

ALL_BUTTONS_TEXT_LIST = [v for k,v in globals().items() if k.startswith('BUTTON_')]

def text_is_button(text):
    return text in ALL_BUTTONS_TEXT_LIST
