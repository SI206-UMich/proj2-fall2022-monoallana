from xml.sax import parseString
from bs4 import BeautifulSoup
import re
import os
import csv
import unittest


def get_listings_from_search_results(html_file):
    """
    Write a function that creates a BeautifulSoup object on html_file. Parse
    through the object and return a list of tuples containing:
     a string of the title of the listing,
     an int of the cost to rent for one night,
     and a string of the listing id number
    in the format given below. Make sure to turn costs into ints.

    The listing id is found in the url of a listing. For example, for
        https://www.airbnb.com/rooms/1944564
    the listing id is 1944564.
.

    [
        ('Title of Listing 1', 'Cost 1', 'Listing ID 1'),  # format
        ('Loft in Mission District', 210, '1944564'),  # example
    ]
    """
    # class with all the things? : lwy0wad l1tup9az dir dir-ltr
    # class in div get id : t1jojoys dir dir-ltr > id : 'title_51027324'
    # class in div : t1jojoys dir dir-ltr > title of listing
    # class in span : _tyxjp1 > listing cost

    with open(html_file) as f:
        tuplst = []
        soup = BeautifulSoup(f, 'html.parser')
        listings_list = soup.find_all("div", class_='lwy0wad l1tup9az dir dir-ltr')

        for listing in listings_list:
            info = listing.find('div', class_='t1jojoys dir dir-ltr')
            idnum = info.get('id')[6:]
            title = info.text
            cost = (listing.find('span', class_='_tyxjp1')).text[1:]
            tuplst.append((title, int(cost), idnum))
            
        return(tuplst)


def get_listing_information(listing_id):
    """
    Write a function to return relevant information in a tuple from an Airbnb listing id.
    NOTE: Use the static files in the html_files folder, do NOT send requests to the actual website.
    Information we're interested in:
        string - Policy number: either a string of the policy number, "Pending", or "Exempt"
            This field can be found in the section about the host.
            Note that this is a text field the lister enters, this could be a policy number, or the word
            "pending" or "exempt" or many others. Look at the raw data, decide how to categorize them into
            the three categories.
        string - Place type: either "Entire Room", "Private Room", or "Shared Room"
            Note that this data field is not explicitly given from this page. Use the
            following to categorize the data into these three fields.
                "Private Room": the listing subtitle has the word "private" in it
                "Shared Room": the listing subtitle has the word "shared" in it
                "Entire Room": the listing subtitle has neither the word "private" nor "shared" in it
        int - Number of bedrooms
.
    (
        policy number,
        place type,
        number of bedrooms
    )
    """
    # policy number : class in li : f19phm7j dir dir-ltr
    # place type : check for words in listing
    # number of bedrooms : regex it

    with open("html_files/listing_"+str(listing_id)+".html") as f:
        soup = BeautifulSoup(f, 'html.parser')

        # finding room policy...
        findpolicynum = soup.find('li', class_='f19phm7j dir dir-ltr')
        policynum = findpolicynum.text[15:]

        if "ending" in policynum:
            policynum = 'Pending'
        elif "not" in policynum:
            policynum = "Exempt"
        else:
            pass

        # finding room type...
        placetype = ""
        search = soup.find('meta', property='og:description')

        if 'Private room' in search.get('content'):
            placetype = 'Private Room'
        elif 'shared' in search.get('content'):
            placetype = 'Shared Room'
        else: 
            placetype = 'Entire Room'

        # finding number of bedrooms...
        bedroom_pattern = r"([0-9]) bed[rooms?]?"
        bedroom_text = soup.find(text=re.compile(bedroom_pattern))
        bedroom_num = bedroom_text[:1]

        return (policynum, placetype, int(bedroom_num))
    


def get_detailed_listing_database(html_file):
    """
    Write a function that calls the above two functions in order to return
    the complete listing information using the functions you???ve created.
    This function takes in a variable representing the location of the search results html file.
    The return value should be in this format:

    [
        (Listing Title 1,Cost 1,Listing ID 1,Policy Number 1,Place Type 1,Number of Bedrooms 1),
        (Listing Title 2,Cost 2,Listing ID 2,Policy Number 2,Place Type 2,Number of Bedrooms 2),
        ...
    ]
    """
    # create new list
    newlst = []

    # get listings from search
    for listing in get_listings_from_search_results(html_file):
        title = listing[0]
        cost = listing[1]
        id = listing[2]

        details = get_listing_information(id)
        policynum = details[0]
        placetype = details[1]
        bedroomnum = details[2]

        # add everything to new list
        newlst.append((title, cost, id, policynum, placetype, bedroomnum))

    return newlst

def write_csv(data, filename):
    """
    Write a function that takes in a list of tuples (called data, i.e. the
    one that is returned by get_detailed_listing_database()), sorts the tuples in
    ascending order by cost, writes the data to a csv file, and saves it
    to the passed filename. The first row of the csv should contain
    "Listing Title", "Cost", "Listing ID", "Policy Number", "Place Type", "Number of Bedrooms",
    respectively as column headers. For each tuple in data, write a new
    row to the csv, placing each element of the tuple in the correct column.

    When you are done your CSV file should look like this:

    Listing Title,Cost,Listing ID,Policy Number,Place Type,Number of Bedrooms
    title1,cost1,id1,policy_number1,place_type1,num_bedrooms1
    title2,cost2,id2,policy_number2,place_type2,num_bedrooms2
    title3,cost3,id3,policy_number3,place_type3,num_bedrooms3
    ...

    In order of least cost to most cost.

    This function should not return anything.
    """
    # create a new file
    f = open(filename, "w")

    # create a list of headers, join the list, and write into the file
    header_list = ["Listing Title", "Cost", "Listing ID", "Policy Number", "Place Type", "Number of Bedrooms"]
    headers = (",").join(header_list)
    f.write(headers + '\n')

    # sort tuple by least costly to most
    info_sort = sorted(data, key=lambda x:x[1])
    for item in info_sort:
        newstr = ''
        for char in str(item):
            if char != "'":
                newstr += char
        new = newstr.split(", ")
        result = ",".join(new)
        f.write(result.strip("[]()") + '\n')


def check_policy_numbers(data):
    """
    Write a function that takes in a list of tuples called data, (i.e. the one that is returned by
    get_detailed_listing_database()), and parses through the policy number of each, validating the
    policy number matches the policy number format. Ignore any pending or exempt listings.
    Return the listing numbers with respective policy numbers that do not match the correct format.
        Policy numbers are a reference to the business license San Francisco requires to operate a
        short-term rental. These come in two forms, where # is a number from [0-9]:
            20##-00####STR
            STR-000####
    .
    Return value should look like this:
    [
        listing id 1,
        listing id 2,
        ...
    ]

    """
    # create regex to check valid policy numbers
    policy_pattern1 = r"20\d{2}\-00\d{4}STR"
    policy_pattern2 = r"STR\-000\d{4}"

    # new list for listing IDs that have policy numbers that do not match the correct format
    newlst = []
    
    # check policy numbers
    for item in data:
        policynum = item[3]
        listid = item[2]
        if re.match(policy_pattern1, policynum):
            pass
        elif re.match(policy_pattern2, policynum):
            pass
        elif policynum == "Pending" or policynum == 'Exempt':
            pass
        else:
            newlst.append(listid)

    return newlst

# def extra_credit(listing_id): did not do to preserve mental energy
#     """
#     There are few exceptions to the requirement of listers obtaining licenses
#     before listing their property for short term leases. One specific exception
#     is if the lister rents the room for less than 90 days of a year.

#     Write a function that takes in a listing id, scrapes the 'reviews' page
#     of the listing id for the months and years of each review (you can find two examples
#     in the html_files folder), and counts the number of reviews the apartment had each year.
#     If for any year, the number of reviews is greater than 90 (assuming very generously that
#     every reviewer only stayed for one day), return False, indicating the lister has
#     gone over their 90 day limit, else return True, indicating the lister has
#     never gone over their limit.
#     """
#     pass


class TestCases(unittest.TestCase):

    def test_get_listings_from_search_results(self):
        # call get_listings_from_search_results("html_files/mission_district_search_results.html")
        # and save to a local variable
        listings = get_listings_from_search_results(
            "html_files/mission_district_search_results.html")
        # check that the number of listings extracted is correct (20 listings)
        self.assertEqual(len(listings), 20)
        # check that the variable you saved after calling the function is a list
        self.assertEqual(type(listings), list)
        # check that each item in the list is a tuple
        for item in listings:
            self.assertEqual(type(item), tuple)
        # check that the first title, cost, and listing id tuple is correct (open the search results html and find it)
        self.assertEqual(listings[0], ('Loft in Mission District', 210, '1944564'))
        # check that the last title is correct (open the search results html and find it)
        self.assertEqual(listings[19], ('Guest suite in Mission District', 238, '32871760'))

    def test_get_listing_information(self):
        html_list = ["1623609",
                     "1944564",
                     "1550913",
                     "4616596",
                     "6600081"]
        # call get_listing_information for i in html_list:
        listing_informations = [
            get_listing_information(id) for id in html_list]
        # check that the number of listing information is correct (5)
        self.assertEqual(len(listing_informations), 5)
        for listing_information in listing_informations:
            # check that each item in the list is a tuple
            self.assertEqual(type(listing_information), tuple)
            # check that each tuple has 3 elements
            self.assertEqual(len(listing_information), 3)
            # check that the first two elements in the tuple are string
            self.assertEqual(type(listing_information[0]), str)
            self.assertEqual(type(listing_information[1]), str)
            # check that the third element in the tuple is an int
            self.assertEqual(type(listing_information[2]), int)
        # check that the first listing in the html_list has policy number 'STR-0001541'
        self.assertEqual(get_listing_information(1623609)[0], 'STR-0001541')
        # check that the last listing in the html_list is a "Private Room"
        self.assertEqual(get_listing_information(6600081)[1], "Private Room")
        # check that the third listing has one bedroom
        self.assertEqual(get_listing_information(1550913)[2], 1)

    def test_get_detailed_listing_database(self):
        # call get_detailed_listing_database on "html_files/mission_district_search_results.html"
        # and save it to a variable
        detailed_database = get_detailed_listing_database(
            "html_files/mission_district_search_results.html")
        # check that we have the right number of listings (20)
        self.assertEqual(len(detailed_database), 20)
        for item in detailed_database:
            # assert each item in the list of listings is a tuple
            self.assertEqual(type(item), tuple)
            # check that each tuple has a length of 6
            self.assertEqual(len(item), 6)
        # check that the first tuple is made up of the following:
        # 'Loft in Mission District', 210, '1944564', '2022-004088STR', 'Entire Room', 1
        self.assertEqual(detailed_database[0], ('Loft in Mission District', 210, '1944564', '2022-004088STR', 'Entire Room', 1))
        # check that the last tuple is made up of the following:
        # 'Guest suite in Mission District', 238, '32871760', 'STR-0004707', 'Entire Room', 1
        self.assertEqual(detailed_database[19], ('Guest suite in Mission District', 238, '32871760', 'STR-0004707', 'Entire Room', 1))


    def test_write_csv(self):
        # call get_detailed_listing_database on "html_files/mission_district_search_results.html"
        # and save the result to a variable
        detailed_database = get_detailed_listing_database(
            "html_files/mission_district_search_results.html")
        # call write csv on the variable you saved
        write_csv(detailed_database, "test.csv")
        # read in the csv that you wrote
        csv_lines = []
        with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'test.csv'), 'r') as f:
            csv_reader = csv.reader(f)
            for i in csv_reader:
                csv_lines.append(i)
        # check that there are 21 lines in the csv
        self.assertEqual(len(csv_lines), 21)
        # check that the header row is correct
        self.assertEqual(csv_lines[0], ['Listing Title','Cost','Listing ID','Policy Number', 'Place Type', 'Number of Bedrooms'])
        # check that the next row is Private room in Mission District,82,51027324,Pending,Private Room,1
        self.assertEqual(csv_lines[1], ['Private room in Mission District','82','51027324','Pending','Private Room','1'])
        # check that the last row is Apartment in Mission District,399,28668414,Pending,Entire Room,2
        self.assertEqual(csv_lines[20], ['Apartment in Mission District','399','28668414','Pending','Entire Room','2'])
    

    def test_check_policy_numbers(self):
        # call get_detailed_listing_database on "html_files/mission_district_search_results.html"
        # and save the result to a variable
        detailed_database = get_detailed_listing_database(
            "html_files/mission_district_search_results.html")
        # call check_policy_numbers on the variable created above and save the result as a variable
        invalid_listings = check_policy_numbers(detailed_database)
        # check that the return value is a list
        self.assertEqual(type(invalid_listings), list)
        # check that there is exactly one element in the string
        self.assertEqual(len(invalid_listings), 1)
        # check that the element in the list is a string
        self.assertEqual(type(invalid_listings[0]), str)
        # check that the first element in the list is '16204265'
        self.assertEqual(invalid_listings[0], '16204265')


if __name__ == '__main__':
    database = get_detailed_listing_database(
        "html_files/mission_district_search_results.html")
    write_csv(database, "airbnb_dataset.csv")
    check_policy_numbers(database)
    unittest.main(verbosity=2)

# print(get_listings_from_search_results(
#     'html_files/mission_district_search_results.html'))
# print(get_listing_information(1944564))
# print(get_listing_information(28668414)) # 2 bed
# print(get_listing_information(11225011)) # private for sure
# print(get_detailed_listing_database('html_files/mission_district_search_results.html'))
# write_csv(get_detailed_listing_database('html_files/mission_district_search_results.html'), 'test_file.csv')
# print(check_policy_numbers(get_detailed_listing_database('html_files/mission_district_search_results.html')))
