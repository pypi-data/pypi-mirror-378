import os
import shutil
import matplotlib.pyplot as plt
import openai
import pandas as pd
import base64
import json
import time
import re


def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()
        base64_encoded = base64.b64encode(image_data).decode("utf-8")

        return base64_encoded

def run_test(root,image,side, creds, genai_key, country):

    start = time.time()
    from idvpackage import ocr
    end = time.time()
    print(f'Time taken to import: {end - start}')

    credentials_string = json.dumps(creds)

    start = time.time()
    try:
        idv = ocr.IdentityVerification(credentials_string, api_key=genai_key, genai_key=genai_key)
    except TypeError:
        idv = ocr.IdentityVerification(credentials_string, api_key=genai_key)
    end = time.time()
    print(f'Time taken to initialize: {end - start}')

    img = image_to_base64(os.path.join(root,image))
    #
    # #=====Extract Front ID=======
    if side == 'front':
        try:
            data = idv.extract_front_id_info(img, country=country, nationality=country)
        except TypeError:
            data = idv.extract_front_id_info(img, country=country)
    if side =='back':
    #=====Extract Back ID=======
        try:
            data = idv.extract_back_id_info(img, country=country, nationality=country)
        except TypeError:
            data = idv.extract_back_id_info(img, country=country)
    elif side=='page1':
    #=====Extract Passport========
        try:
            data= idv.exract_passport_info(img, country=country, nationality=country)
        except TypeError:
            data= idv.exract_passport_info(img, country=country)
    elif side=='auto':
        try:
            data = idv.extract_document_info(img, side=side, document_type='national_id', country=country,nationality=country)
        except TypeError:
            data = idv.extract_document_info(img, side=side, document_type='national_id', country=country, nationality=country)

    return data


def run_test_agent(root,image,side, creds,api_key, genai_key, country, nationality, step_data=None):

    start = time.time()
    from idvpackage import ocr
    end = time.time()
    print(f'Time taken to import: {end - start}')

    credentials_string = json.dumps(creds)

    start = time.time()
    try:
        idv = ocr.IdentityVerification(credentials_string, api_key=genai_key, genai_key=api_key)
    except TypeError:
        idv = ocr.IdentityVerification(credentials_string, api_key=genai_key)
    end = time.time()
    print(f'Time taken to initialize: {end - start}')

    img = image_to_base64(os.path.join(root,image))

    if side=='front' or side=='back':
        try:
            data = idv.extract_document_info(img, side=side, document_type='national_id', country=country,nationality=nationality)
        except TypeError:
            data = idv.extract_document_info(img, side=side, document_type='national_id', country=country)

    if side=='auto':
        try:
            data = idv.extract_document_info(img, side=side, document_type='', country=country,nationality=nationality)
        except TypeError:
            data = idv.extract_document_info(img, side=side, document_type='', country=country)


    if side=='page1' or side=='page2':
        try:
            data = idv.extract_document_info(img, side=side, document_type='passport', country=country,nationality=nationality, step_data=step_data)
        except TypeError:
            data = idv.extract_document_info(img, side=side, document_type='passport', country=country)

    return data




genai_key = ''
api_key = "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"
#api_key = 'AIzaSyA3nIy5Hx_80EnF_kJWZPOEkLLFuQw_yms'

creds = {
    "type": "service_account",
    "project_id": "spotii-me",
    "private_key_id": "c5168da8dc8d959c80d9d42346baf5312397029d",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC0od0ekJRVtPji\n+vh20vJr1uYQCWpZPcD9Te+wnObwD+M9x7EFp5oyU2l8vm5sq0Vvez1T/AvyWgr8\nGH9N8ssetpBUbX2ftlk81X3P1Lz73GXMFCFh/7gS0h6HuG0LUdx9pUGdykv2kMa1\nSU9Wnm5XbL+SzbgHDHDkxPeiDAHUfO7yEG+jtafslH08pj1LYO0ir4JBqAOUqy5G\nPTj2zpx7AUL7EZ23x5q/aGycMs2I6yIANAwT35HyMn1UtrwOsjyspH99mj+1KEmL\nuBZFG/+CYlcKUl7PKl3yvcbDBzrNGH6sRdBJve6mfhgVddgWSAT/V1FhMJU76wP2\n4MZQjQUbAgMBAAECggEAN+7FPzEq1Y1H4lUvee/hJDZzn/Sia0bdizJGbcxwEFcD\nGT7MGIGpFDtS908qd1jjk904BNkPw/hQ3XYieXscnYKPl60d0MZQxK8hGal46Y56\nMSLsoWFjWOSakpEvpuku2vNAqcEaG5wCA+HTAPHnHggtHCK6gOg/zv8U5SdNq8OM\nsTHO5Yx7xPu90b8MEh49B6w2MTRx/dKMhpo/1RQWOJLZc30ndY348Q+Xh7eCRzIh\npJAOYV/y3zOWOf//G6squ22gvX6jqCUjkQktsmdjNzdyn4l5B+wqgr/Lo0gxMxE+\n3SXktEVEXsdl863pxTSbcmRpADcggd+VMdRMv4IvaQKBgQDTFe7r0ZvWF6Kbq9i0\n2KfhkZNYCdQKj0o8q1/1pl7bBvg4ytp5iUtakf8gNDUUDFuLbpZ9iDExyEZPyFLt\nKHqMk+vquJtv3xHkbUrRlE27z1imJAp/hZAGVF4oo2ac0HajNP+jo8C5d8CQjeuw\n2aIwm8LqDtHO7qWWBVU5IW41+QKBgQDbERnMviiDEKAtUw4Ci6Ig3kDU7hEtegJP\nEq1Lsu8840dZxXXuus7L0trhtKhUBcSKiCIDhJgAAuLoKlz4Nf8xguoxfSe4UY1G\nYWiivwJOPN9LYA0KuMtToIoWSrjTSAtwOM1QKdvr7wgmWYqNIDJLXCHmU6Ylk2CT\naSwMspmIswKBgAGoo3cA76uQBfwZLpvFNBSGs1S2xw7KL3golJl2lDo+ZMb1eSAJ\nXyk4CnwzTNN6gWGoHdCguFo+y6am2Vf5wHTIWMtAZiBL7XUREsxw0OeP6o9rqxVz\ndD1IfnDtT8odrUD9EqEzkTkj4sSACQEbxLWDE9YJBccNgwmZwyCuzZHpAoGBALs+\nra+8ZgJJJrA3CoWQdn7jmcSmzFXzsJ+H1koa4rRHjAgmaHwqfnHng6FienJ/D5Rd\ncb1SC14PGYXaF+csuDjIroaodFfulPOwdPCOlVjsXOwfaGZet6R+VylgqwQk02oT\nkyJO9SSABpZI+M1R1MtnL66glyYNB4JYZgdgbS1TAoGBAL65fpY8BqFDfXyW0d7P\nUbBPEiWGDsweT3wm5MEvprgmSxOg5ndHX280cP99EYBaED+Xja0pU1wd48VRVfHb\n2xEJ9gr5m9cHQC4dXjbIIx/nCG6lpSA6Jd8JAds/DUn7mCy2YxNCNFJbbuSMX85C\nBDbfocMiMz1Gr3YB/sFSyjKD\n-----END PRIVATE KEY-----\n",
    "client_email": "spotii-gapi-10-2023@spotii-me.iam.gserviceaccount.com",
    "client_id": "111897133454311774587",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/spotii-gapi-10-2023%40spotii-me.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}

root =  "/Users/husunshujaat/Downloads/iraq_passport_new_idv/yaseen/"
images = ['yaseen_passport.png']
print(len(images))
country='IRQ'
nationality = None

outputs = []

step_data = {'error': '', 'error_details': '', 'id_number_front': '199466850595', 'card_number_front': 'A38082126', 'first_name': 'ياسين', 'first_name_en': 'Yasin', 'father_name': 'أيمن', 'father_name_en': 'Ayman', 'third_name': 'محمد', 'third_name_en': 'Muhammad', 'last_name': 'العبيدي', 'last_name_en': 'Al-Ubaidi', 'mother_first_name': 'سهاد', 'mother_first_name_en': 'Suhad', 'mother_last_name': 'منذر', 'mother_last_name_en': 'Munthir', 'gender_ar': 'ذكر', 'gender': 'male', 'blood_type': '+A', 'serial_number': '895932', 'doc_type': 'national_identity_card', 'nationality': 'IRQ', 'nationality_en': 'IRQ', 'name': 'ياسين أيمن العبيدي', 'name_en': 'Yasin Ayman Al-Ubaidi', 'front_extracted_data': 'کوماری عیراق / وه زاره تی ناوخو\nبه ریوه به رایه تی باری شارستانی و پاسپورت و نیشنگه\nجمهورية العراق / وزارة الداخلية\nمديرية الأحوال المدنية والجوازات والاقامة\nA\nالبطاقة الوطنية / كارتى نيشتماني\n199466850595\nالاسم / ناو : ياسين\nالأب / باوك : أيمن\nالجد / بابير : محمد\nاللقب / نازناو : العبيدي\nالأم / دايك : سهاد\nالجد / بابير : منذر\nالجنس / ردگه ز : ذكر\nفصيلة الدم/ گروبی خوین : +A\n895932\nA38082126', 'translated_front_id_text': '', 'front_coloured': True, 'back_coloured': True, 'front_doc_on_pp': 'clear', 'front_logo_result': 'clear', 'front_template_result': 'clear', 'front_screenshot_result': '', 'front_photo_on_screen_result': '', 'front_blurred': '', 'front_glare': '', 'front_face_locations': '[[233, 290, 444, 130]]', 'front_face_encodings': '[[-0.09408826380968094, 0.04781844839453697, -0.013824906200170517, -0.08345187455415726, -0.017775898799300194, -0.0483972392976284, -0.020767023786902428, -0.05839747563004494, 0.15469390153884888, -0.10424301773309708, 0.19467416405677795, 0.03725694119930267, -0.1513485461473465, 0.011208387091755867, 0.0416281633079052, 0.05367797240614891, -0.11147508770227432, -0.11714450269937515, -0.08254285901784897, -0.07985847443342209, 0.04592445120215416, -0.01622769981622696, -0.035448651760816574, 0.08820640295743942, -0.191756010055542, -0.22217640280723572, -0.12351930886507034, -0.16686266660690308, 0.022918468341231346, -0.09160386025905609, 0.038566406816244125, -0.02938525378704071, -0.07052832841873169, -0.006017150357365608, 0.023745408281683922, 0.02207256853580475, 0.028494635596871376, -0.05455142259597778, 0.2599770426750183, 0.023620178923010826, -0.10417480766773224, -0.005270997062325478, 0.051092226058244705, 0.322055459022522, 0.11028201878070831, 0.0023632515221834183, 0.080568827688694, -0.0697847306728363, 0.16007457673549652, -0.21346215903759003, 0.12784980237483978, 0.07764882594347, 0.1607542484998703, 0.07900616526603699, 0.15842433273792267, -0.1276003122329712, 0.09452615678310394, 0.14244139194488525, -0.24831683933734894, 0.19174841046333313, 0.07402855902910233, 0.003282397985458374, -0.033008117228746414, -0.05032682791352272, 0.25342902541160583, 0.12469416111707687, -0.12812265753746033, -0.13730180263519287, 0.12449483573436737, -0.1373712569475174, -0.1116243526339531, 0.04866583272814751, -0.11961105465888977, -0.2054165005683899, -0.24921493232250214, 0.06699132174253464, 0.3442019820213318, 0.28634876012802124, -0.2305937260389328, 0.06536684185266495, -0.09966279566287994, -0.0645868182182312, 0.10166306793689728, 0.015628870576620102, -0.101566843688488, -0.002082051942124963, -0.09361822158098221, 0.03001396916806698, 0.21635660529136658, 0.04645422846078873, -0.03522661700844765, 0.19544003903865814, 0.008467230014503002, -0.02744390070438385, -0.0038488840218633413, 0.017343277111649513, -0.18570847809314728, -0.019776666536927223, -0.09770530462265015, -0.06489195674657822, 0.08375894278287888, -0.04728102311491966, 0.05989043787121773, 0.13237592577934265, -0.2406751811504364, 0.19135914742946625, -0.049121465533971786, -0.047503065317869186, -0.03846914321184158, 0.11838695406913757, -0.14264266192913055, -0.01312190666794777, 0.15403597056865692, -0.22921541333198547, 0.13694877922534943, 0.12827341258525848, 0.07699238508939743, 0.09985792636871338, 0.06728686392307281, 0.041923947632312775, -0.003312612185254693, 0.029155751690268517, -0.17266811430454254, -0.04593943804502487, 0.026180682703852654, 0.004961944185197353, 0.10467945784330368, 0.06830030679702759]]', 'front_tampered_result': 'clear', 'issuing_country': 'IRQ', 'valid_nationality': 'valid_nationality_result'}

step_data= None



for image in images:
    #data_legacy = run_test(root,image, side='page1', creds=creds, genai_key=genai_key, country=country)
    starting_point = time.time()
    data_agent = run_test_agent(root,image,side='page1', creds=creds, api_key=api_key, genai_key=genai_key, country=country, nationality=nationality,step_data=step_data)
    end = time.time()
    time_taken = end-starting_point
    print(time_taken)
    print(f'file:{image}')
    print("Data Agent:", data_agent)
    # if data_agent['error']=='':
    #     print(data_agent['mrz1'],'+', data_agent['mrz2'],'+', data_agent['mrz3'])
    data_agent['file'] = image
    outputs.append(data_agent)




#pd.DataFrame(outputs).to_csv("/Users/husunshujaat/Downloads/lbn_passport_test.csv")

#Test:
"""
2. IRQ Passport
3. LBN Passport
4. SDN Passport
5. SYR Passport
6. JOR Passport
7. PSE Passport
8. Expired Passports

National ID
1. Front + Back IRQ National ID
"""

ocr_text = """
State Of Qatar
Residency Permit
Statt
ID.No:
28776002462
D.O.B:
25/10/1987
Expiry:
11/01/2026
Nationality:
Occupation:
سوري
SYRIA
of
Qatar
دولة قطر
رخصة إقامة
الرقم الشخصي
تاريخ الميلاد:
الصلاحية
الجنسية:
المهنة
مدرس رياضيا
الإسم: خالد صيحان العبد العزيز
Name: KHALED SIJAN ALABDULAZIZ
"""


# data_agent_new = {'error': '', 'error_details': '', 'id_number_front': '199089705180', 'card_number_front': 'AJ8557785', 'first_name': 'بلال', 'first_name_en': 'Bilal', 'father_name': 'عامر', 'father_name_en': 'Amer', 'third_name': 'محمد', 'third_name_en': 'Mohammed', 'last_name': 'العزاوي', 'last_name_en': 'Al-Azzawi', 'mother_first_name': 'نداء', 'mother_first_name_en': 'Nidaa', 'mother_last_name': 'ناصر', 'mother_last_name_en': 'Nasser', 'gender_ar': 'ذكر', 'gender': 'male', 'blood_type': 'O', 'serial_number': '', 'doc_type': 'national_identity_card', 'nationality': 'IRQ', 'nationality_en': 'IRQ', 'name': 'بلال عامر العزاوي', 'name_en': 'Bilal Amer Al-Azzawi', 'front_extracted_data': 'جمهورية العراق / كومارى عيراق\nوزارة الداخلية / وەزارەتى ناوخو\nالاسم / ناو : بلال\nالأب / باوك : عامر\nالجد / بابير : محمد\nالبطاقة الوطنية / كارني\nمديرية الجنسية العامة\nبیریز میم رایاتی گشتی بر نگار نامه\n199089705180\nاللقب / نازناو : العزاوي\nالأم / دايك : نداء\nالجد / بابير : ناصر\nالجنس / رمز : ذكر\nفصيلة الدم/ گروبي خوين : 0\nAJ8557785', 'translated_front_id_text': '', 'front_coloured': True, 'back_coloured': True, 'front_doc_on_pp': 'clear', 'front_logo_result': 'clear', 'front_template_result': 'clear', 'front_screenshot_result': 'clear', 'front_photo_on_screen_result': 'clear', 'front_blurred': 'clear', 'front_glare': 'clear', 'front_face_locations': '[[125, 107, 224, 34]]', 'front_face_encodings': '[[-0.10338075459003448, 0.14578396081924438, 0.08440461754798889, -0.14605315029621124, -0.07728587090969086, -0.007242473773658276, -0.008862236514687538, -0.040224917232990265, 0.21329447627067566, -0.019070159643888474, 0.23413123190402985, 0.02645161561667919, -0.2096935212612152, -0.04236436262726784, 0.03522923216223717, 0.073409803211689, -0.19081979990005493, -0.061631496995687485, -0.025643637403845787, -0.08665827661752701, 0.03180794045329094, 0.04158361628651619, 0.11483301222324371, 0.015252680517733097, -0.11866310983896255, -0.3843784034252167, -0.07082019001245499, -0.11494867503643036, 0.1052173301577568, -0.11641714721918106, 0.06066722422838211, 0.004927462432533503, -0.1414071023464203, -0.018532700836658478, -0.021959513425827026, 0.0867014229297638, -0.0636298730969429, -0.06844110786914825, 0.22961203753948212, 0.0014244673075154424, -0.14490997791290283, 0.04284915328025818, 0.03206323832273483, 0.27246272563934326, 0.16646306216716766, 0.00908429641276598, 0.08088627457618713, -0.07722512632608414, 0.12837809324264526, -0.21485482156276703, 0.1859176754951477, 0.09845980256795883, 0.14346027374267578, -0.010211015120148659, 0.1132977157831192, -0.14860503375530243, -0.036888159811496735, 0.16258853673934937, -0.2784234881401062, 0.15115107595920563, 0.1418038308620453, -0.006882551591843367, -0.06375027447938919, -0.056210171431303024, 0.18128594756126404, 0.15923236310482025, -0.17005446553230286, -0.13601963222026825, 0.09231147915124893, -0.09972874820232391, -0.014746789820492268, 0.07495158910751343, -0.108131043612957, -0.2035558819770813, -0.2061217725276947, 0.1485489308834076, 0.3332235515117645, 0.13277705013751984, -0.16884519159793854, -0.034240104258060455, -0.07452703267335892, -0.03606678918004036, 0.037441324442625046, 0.08154100179672241, -0.11639115959405899, -0.059341561049222946, -0.11272046715021133, 0.05262646824121475, 0.10150162875652313, -0.01275008823722601, -0.07367321103811264, 0.2226407378911972, 0.008517914451658726, 0.053896088153123856, -0.056915149092674255, 0.08242812007665634, -0.19609607756137848, 0.0658753290772438, -0.15108339488506317, -0.0064195371232926846, 0.03170144185423851, -0.08067114651203156, -0.02434239722788334, 0.07204984128475189, -0.16979488730430603, 0.18769438564777374, 0.0015946191269904375, -0.06802070140838623, -0.006363314110785723, -0.000990344095043838, -0.10280732065439224, -0.04766012728214264, 0.15146756172180176, -0.2721529006958008, 0.20902280509471893, 0.17280267179012299, 0.06903448700904846, 0.20497949421405792, 0.10668903589248657, 0.052189137786626816, 0.10862745344638824, -0.007052598986774683, -0.12816080451011658, -0.015955518931150436, 0.022478483617305756, -0.011407117359340191, 0.058699991554021835, 0.05927924066781998]]', 'front_tampered_result': 'clear', 'issuing_country': 'IRQ', 'valid_nationality': 'clear', 'time_taken': 14.23398470878601}
#
# data_agent_old=  {'error': '', 'error_details': '', 'id_number_front': '199089705180', 'card_number_front': 'AJ8557785', 'first_name': 'بلال', 'first_name_en': 'Bilal', 'father_name': 'عامر', 'father_name_en': 'Amer', 'third_name': 'محمد', 'third_name_en': 'Mohammed', 'last_name': 'العزاوي', 'last_name_en': 'Al-Azzawi', 'mother_first_name': 'نداء', 'mother_first_name_en': 'Nidaa', 'mother_last_name': 'ناصر', 'mother_last_name_en': 'Nasser', 'gender_ar': 'ذكر', 'gender': 'male', 'blood_type': 'O', 'serial_number': '', 'doc_type': 'national_identity_card', 'nationality': 'IRQ', 'nationality_en': 'IRQ', 'name': 'بلال عامر العزاوي', 'name_en': 'Bilal Amer Al-Azzawi', 'front_extracted_data': 'جمهورية العراق / كومارى عيراق\nوزارة الداخلية / وەزارەتى ناوخو\nالاسم / ناو : بلال\nالأب / باوك : عامر\nالجد / بابير : محمد\nالبطاقة الوطنية / كارني\nمديرية الجنسية العامة\nبیریز میم رایاتی گشتی بر نگار نامه\n199089705180\nاللقب / نازناو : العزاوي\nالأم / دايك : نداء\nالجد / بابير : ناصر\nالجنس / رمز : ذكر\nفصيلة الدم/ گروبي خوين : 0\nAJ8557785', 'translated_front_id_text': '', 'front_coloured': True, 'back_coloured': True, 'front_doc_on_pp': 'clear', 'front_logo_result': 'clear', 'front_template_result': 'clear', 'front_screenshot_result': 'clear', 'front_photo_on_screen_result': 'clear', 'front_blurred': 'clear', 'front_glare': 'clear', 'front_face_locations': '[[125, 107, 224, 34]]', 'front_face_encodings': '[[-0.10338075459003448, 0.14578396081924438, 0.08440461754798889, -0.14605315029621124, -0.07728587090969086, -0.007242473773658276, -0.008862236514687538, -0.040224917232990265, 0.21329447627067566, -0.019070159643888474, 0.23413123190402985, 0.02645161561667919, -0.2096935212612152, -0.04236436262726784, 0.03522923216223717, 0.073409803211689, -0.19081979990005493, -0.061631496995687485, -0.025643637403845787, -0.08665827661752701, 0.03180794045329094, 0.04158361628651619, 0.11483301222324371, 0.015252680517733097, -0.11866310983896255, -0.3843784034252167, -0.07082019001245499, -0.11494867503643036, 0.1052173301577568, -0.11641714721918106, 0.06066722422838211, 0.004927462432533503, -0.1414071023464203, -0.018532700836658478, -0.021959513425827026, 0.0867014229297638, -0.0636298730969429, -0.06844110786914825, 0.22961203753948212, 0.0014244673075154424, -0.14490997791290283, 0.04284915328025818, 0.03206323832273483, 0.27246272563934326, 0.16646306216716766, 0.00908429641276598, 0.08088627457618713, -0.07722512632608414, 0.12837809324264526, -0.21485482156276703, 0.1859176754951477, 0.09845980256795883, 0.14346027374267578, -0.010211015120148659, 0.1132977157831192, -0.14860503375530243, -0.036888159811496735, 0.16258853673934937, -0.2784234881401062, 0.15115107595920563, 0.1418038308620453, -0.006882551591843367, -0.06375027447938919, -0.056210171431303024, 0.18128594756126404, 0.15923236310482025, -0.17005446553230286, -0.13601963222026825, 0.09231147915124893, -0.09972874820232391, -0.014746789820492268, 0.07495158910751343, -0.108131043612957, -0.2035558819770813, -0.2061217725276947, 0.1485489308834076, 0.3332235515117645, 0.13277705013751984, -0.16884519159793854, -0.034240104258060455, -0.07452703267335892, -0.03606678918004036, 0.037441324442625046, 0.08154100179672241, -0.11639115959405899, -0.059341561049222946, -0.11272046715021133, 0.05262646824121475, 0.10150162875652313, -0.01275008823722601, -0.07367321103811264, 0.2226407378911972, 0.008517914451658726, 0.053896088153123856, -0.056915149092674255, 0.08242812007665634, -0.19609607756137848, 0.0658753290772438, -0.15108339488506317, -0.0064195371232926846, 0.03170144185423851, -0.08067114651203156, -0.02434239722788334, 0.07204984128475189, -0.16979488730430603, 0.18769438564777374, 0.0015946191269904375, -0.06802070140838623, -0.006363314110785723, -0.000990344095043838, -0.10280732065439224, -0.04766012728214264, 0.15146756172180176, -0.2721529006958008, 0.20902280509471893, 0.17280267179012299, 0.06903448700904846, 0.20497949421405792, 0.10668903589248657, 0.052189137786626816, 0.10862745344638824, -0.007052598986774683, -0.12816080451011658, -0.015955518931150436, 0.022478483617305756, -0.011407117359340191, 0.058699991554021835, 0.05927924066781998]]', 'front_tampered_result': 'clear', 'issuing_country': 'IRQ', 'valid_nationality': 'clear', 'time_taken': 11.436336278915405}

"""
Total Time taken in dev: 21.408347368240356 seconds
"""