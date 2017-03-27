import urllib, hashlib, random, string, requests, shutil, os, selenium.webdriver, difflib
from bs4 import BeautifulSoup
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

'''''''''
Method to generate hash
# sha512(key|txnid|amount|productinfo|firstname|email|udf1|udf2|udf3|udf4|udf5||||||SALT)
@hash_params - should be array inside array with the required sequence
@salt - merchant salt
'''''''''


def calculate_hash(hash_params, salt):
    hash_string = ''

    for i in hash_params:
        hash_string += i[1] + '|'

    hash_string += '|||||' + salt

    return hashlib.sha512(hash_string).hexdigest()


def get_post_data(hash_params, surl, furl, pg, bankcode, hash):
    post_data = '';
    for i in hash_params:
        post_data += i[0] + "=" + i[1] + "&"

    return post_data + 'surl=' + urllib.quote_plus(surl) + "&furl=" + urllib.quote_plus(
        furl) + "&pg=" + pg + "&bankcode=" + bankcode + "&hash=" + hash


def write_file(path, data):
    with open(path, 'w') as f:
        f.write(data)


def prepare_files(previous_path, current_path, output_path):
    # if previous folder is not empty remove all the files.
    # Move all the files of current to previous.

    if os.path.isdir(previous_path):
        shutil.rmtree(previous_path)

    if os.path.isdir(current_path):
        os.rename(current_path, previous_path)
    os.makedirs(current_path)

    if os.path.isdir(output_path):
        shutil.rmtree(output_path)
    os.makedirs(output_path)


def get_html_content_using_request(post_params, payu_production_url):
    user_agent = 'Mozilla/5.0 (Linux; Android 5.0; en-us; Xoom Build/HRI39) AppleWebKit/534.13 (KHTML, like Gecko) Version/4.0 Safari/534.13'

    headers = {'User-Agent': user_agent}

    payu_request = requests.post(payu_production_url, data=post_params, headers=headers)

    payu_soup = BeautifulSoup(payu_request.text, "html.parser");

    payu_form = payu_soup.find_all("form")
    bank_url = payu_form[0].get('action')

    bank_request = requests.post(bank_url, headers=headers)
    return u' '.join(bank_request.text).encode('utf-8');


# get_html_content_using_request(pg_codes[0], "HDFB")

def create_web_driver_start_file(payu_production_url, data, surl, furl, pg, bankcode, hash, phantom_js_start_file_name):
    html_content = '<html>' + '\n' + '<body>' + '\n' + '<form action=' + payu_production_url + ' method=post>' + '\n'

    for i in data:
        html_content += '<input type="text" id="' + i[0] + '" name="' + i[0] + '" value="' + i[1] + '"> <br>' + '\n'

    html_content += '<input type="text" id="surl" name="surl" value="' + surl + '"> <br>' + '\n'
    html_content += '<input type="text" id="furl" name="furl" value="' + furl + '"> <br>' + '\n'
    html_content += '<input type="text" id="pg" name="pg" value="' + pg + '"> <br>' + '\n'
    html_content += '<input type="text" id="bankcode" name="bankcode" value="' + bankcode + '"> <br>' + '\n'
    html_content += '<input type="text" id="hash" name="hash" value="' + hash + '"> <br>' + '\n'
    html_content += '<button type="submit" id="pay_button">Pay</button>' + '\n'

    html_content += '</form> </body> </html>'

    write_file(phantom_js_start_file_name, html_content);


def get_html_content_using_phantom_js(file):

    user_agent = 'Mozilla/5.0 (Linux; Android 5.0; en-us; Xoom Build/HRI39) AppleWebKit/534.13 (KHTML, like Gecko) Version/4.0 Safari/534.13'

    # driver = selenium.webdriver.PhantomJS()

    caps = DesiredCapabilities.PHANTOMJS
    caps["phantomjs.page.settings.userAgent"] = user_agent
    driver = selenium.webdriver.PhantomJS(desired_capabilities=caps)

    # do some processing
    driver.get(file);
    p = driver.find_element_by_id("pay_button")
    p.submit()

    page_source = u' '.join(driver.page_source).encode('utf-8');
    driver.execute_script("console.log('hi')");
    driver.quit()
    return page_source


# get_html_content_using_phantom_js(pg_codes[0], "HDFB")

# for bank_code in bank_codes_nb:
#     get_html_content_using_phantom_js(pg_codes[0], bank_code)

# get_html_content_using_phantom_js(pg_codes[0], "HDFB")

# for bank_code in bank_codes_nb:
#     get_html_content(pg_codes[0], bank_code)


# pass absolute path to the files eg, bank_files/output/bank1.html
def compare_files(file1, file2, output_file):
    file1 = open(file1, 'r').readlines()
    file2 = open(file2, 'r').readlines()

    htmlDiffer = difflib.HtmlDiff()
    htmldiffs = htmlDiffer.make_file(file1, file2)

    write_file(output_file, htmldiffs)


# compare_files(current_path + '/' + 'HDFB.html', previous_path + '/' + 'HDFB.html', output_path + '/' + 'HDFB.html')


def run_cb_on_js(file):
    file

'''''
This is app's starting point.
pass true for running the app in debug mode.
debug mode will print the results.
'''''


def main():
    # Files paths
    previous_path = 'bank_files/previous'
    current_path = 'bank_files/current'
    output_path = "bank_files/output"

    prepare_files(previous_path, current_path, output_path)

    # Payu Production url for all modes of payment.
    payu_production_url = "https://secure.payu.in/_payment";

    # Payu bank codes - will keep growing.
    bank_codes_nb = ["ALLB", "ADBB", "AXIB", "BBKB", "BOIB", "BOMB", "CABB", "CSBN", "CBIB", "CUBB", "CRPB", "CSMSNB",
                     "DCBCORP", "DCBB", "DENN", "DSHB", "DLSB", "FEDB", "HDFB", "ICIB", "IDBB", "IDFCNB", "INDB"];

    bank_codes_nb_top = ["AXIB", "HDFB", "ICIB", "YESB", "SBIB"]

    # Payu pg codes for all modes of payments.
    pg_codes = ["NB"];

    salt = '13p0PXZk';
    surl = 'https://payu.herokuapp.com/success'
    furl = 'https://payu.herokuapp.com/failure'

    # have put the files in hash generation order.
    data_required_for_hash = [['key', '0MQaQP'],
                              ['txnid', ''.join(random.sample(string.lowercase + string.digits, 10))],
                              ['amount', '10.0'],
                              ['productinfo', ''.join(random.sample(string.lowercase, 5))],
                              ['firstname', ''.join(random.sample(string.lowercase, 3))],
                              ['email', 'test@itsme.com'],
                              ['udf1', ''],
                              ['udf2', ''],
                              ['udf3', ''],
                              ['udf4', ''],
                              ['udf5', '']];

    phantom_js_start_file_name = "start.html"

    # for all the bank_codes
    for bank_code in bank_codes_nb_top:
        # This method will create start.html file with all required params.
        # By submitting this html file, we will land on bank's page.

        '''''''''''''''''''''''''''''''''
        Using Request to get bank source
        This does not work well,
        Dont try it in HOME:
        '''''''''''''''''''''''''''''''''
        # post_params = get_post_data(data_required_for_hash, surl, furl, pg_codes[0], bank_code,
        #                             calculate_hash(data_required_for_hash, salt))
        # print post_params
        #
        # bank_page_source = get_html_content_using_request(post_params, payu_production_url)

        '''''''''''''''''''''''''''''''''''
        Using Phantom Js to get bank source
        '''''''''''''''''''''''''''''''''''
        create_web_driver_start_file(payu_production_url, data_required_for_hash, surl, furl, pg_codes[0], bank_code,
                                     calculate_hash(data_required_for_hash, salt), phantom_js_start_file_name);

        bank_page_source = get_html_content_using_phantom_js(phantom_js_start_file_name)

        write_file(current_path + '/' + bank_code + '.html', bank_page_source)

        # if os.path.isfile(previous_path + '/' + bank_code + '.html'):
        #     compare_files(current_path + '/' + bank_code + '.html', previous_path + '/' + bank_code + '.html', output_path + '/' + bank_code + '.html')
        # else:
        #     print 'Could not compare "' + previous_path + '/' + bank_code + '.html" does not exist!'

        # let us run the bank js on page source to check whether cb is working fine or not!

        # result = run_cb_js_on(current_path + '/' + bank_code + '.html')

main()
