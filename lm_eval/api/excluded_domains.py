import json

def getExDomains():
    with open("./lm_eval/api/excluded_domains.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    result = list(data.keys())
    return result

excludedDomains = getExDomains()


# excluded_domains = [
#     "www.crackap.com","global.oup.com","nlp.stanford.edu","learninglink.oup.com","content.randomhouse.com","www.brainscape.com",
#     "github.com","arxiv.org","huggingface.co","www.kaggle.com","www.doe.mass.edu","www.baamboozle.com","www.electrical4u.com","web2.0calc.com",
#     "paperswithcode.com","www.solpass.org","www.questionai.com", "quizlet.com", "testbook.com","www.doorsteptutor.com","www.cliffsnotes.com",
#     "quizizz.com","brainly.com", "www.gauthmath.com","www.coursehero.com","www.numerade.com","psychologic.science","mcqmate.com","triyambak.org",
#     "testmoz.com", "www.classace.io","brainly.in","studylib.net","homework.study.com","www.answers.com","www.cambridge.org","schoolbag.info",
#     "askfilo.com","brainly.ph","www.studyadda.com","www.classtools.net","www.helpteaching.com","s3-eu-west-1.amazonaws.com",
#     "www.chegg.com","smart.gov.qa","slideplayer.com","www.proprofs.com","www.studystack.com","www.bartleby.com","praxis.ets.org",
#     "www.triand.com","practicequiz.com","resources.quizalize.com","www.fatskills.com","www.doubtnut.com","compsciedu.com","pakmcqs.com",
#     "www.summitlearning.org","reviewgamezone.com","www.scribd.com","www.coursesidekick.com","fiatlux-day.org","www.mbamcq.com",
#     "www.henry.k12.ga.us","bpsscience.weebly.com","www.nysedregents.org","www.quora.com","www.toppr.com","www.examveda.com",
#     "app.formative.com","nnhsrasetti.pbworks.com","mcdowellscienceexam.weebly.com","bms-et.org","core-docs.s3.us-east-1.amazonaws.com",
#     "michaelynaucoin.weebly.com","questtech.ca","www.studocu.com","www.easynotecards.com","www.bissoy.com","learninglink-oup-com.libproxy.ucl.ac.uk",
# ]


# {
#     "quizlet.com": {
#         "count": 529,
#         "arc_easy": 279,
#         "arc_challenge": 250
#     },
#     "brainly.com": {
#         "count": 301,
#         "arc_easy": 108,
#         "arc_challenge": 193
#     },
#     "www.gauthmath.com": {
#         "count": 207,
#         "arc_easy": 79,
#         "arc_challenge": 128
#     },
#     "quizizz.com": {
#         "count": 84,
#         "arc_easy": 37,
#         "arc_challenge": 47
#     },
#     "huggingface.co": {
#         "count": 55,
#         "arc_challenge": 55
#     },
#     "www.oxen.ai": {
#         "count": 23,
#         "arc_challenge": 23
#     }
# }
