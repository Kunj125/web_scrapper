import requests
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

USERNAME = 'username'
PASSWORD = 'password'

LOGIN_URL = 'https://login.manchester.ac.uk/cas/login?service=https%3A%2F%2Fstudentnet.cs.manchester.ac.uk%2Fugt%2Fyear3%2Fproject%2Fprojectbooktitles.php%3Fyear%3D2024'
URL = 'https://studentnet.cs.manchester.ac.uk/ugt/year3/project/projectbooktitles.php?year=2024'

session = requests.Session()


def login(session, username, password):
    response = session.get(LOGIN_URL)
    soup = BeautifulSoup(response.content, 'html.parser')
    print(soup)
    lt_element = soup.find('input', {'name': 'lt'})
    execution_element = soup.find('input', {'name': 'execution'})

    if lt_element and execution_element:
        lt = lt_element['value']
        execution = execution_element['value']

        login_data = {
            'username': username,
            'password': password,
            'lt': lt,
            'execution': execution,
            '_eventId': 'submit'
        }

        response = session.post(LOGIN_URL, data=login_data)

        if response.status_code == 200:
            return True
        else:
            return False
    else:
        print("Required form elements not found.")
        return False


def scrape_projects(session, url):
    try:
        response = session.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        projects = []

        for project_div in soup.find_all('div', {'style': 'padding : 15px 15px; background-color : #F0F0F0; margin : 15px 10px 15px 10px; border : 1px dashed #A0A0A0; clear : right;'}):
            project_title = project_div.find('p').a.text
            project_id = project_div.find('p')['data-project-title']
            project_url = project_div.find('p').a['href']

            description = scrape_project_details(session, project_url)

            projects.append({
                'id': project_id,
                'title': project_title,
                'description': description
            })

        return projects

    except Exception as e:
        print(f"Error scraping projects: {e}")
        return []


def scrape_project_details(session, url):
    try:
        response = session.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        description_div = soup.find(
            'div', {'data-project-details-description': True})

        if description_div:
            description = description_div.text.strip()
            return description
        else:
            print("Description not found.")
            return ""

    except Exception as e:
        print(f"Error scraping project details: {e}")
        return ""


def generate_pdf(projects):
    pdf = SimpleDocTemplate("projects.pdf", pagesize=letter)
    styles = getSampleStyleSheet()
    title_style = styles["Heading1"]
    description_style = ParagraphStyle(
        "description_style",
        parent=styles["BodyText"],
        fontSize=10,
        leading=12,
    )
    content = []

    for project in projects:
        title = project["title"]
        description = project["description"]

        title_para = Paragraph(title, title_style)
        description_para = Paragraph(description, description_style)

        content.append(title_para)
        content.append(Spacer(1, 12))
        content.append(description_para)
        content.append(Spacer(1, 20))
    pdf.build(content)


def main():
    if login(session, USERNAME, PASSWORD):
        print("Login successful")

        projects = scrape_projects(session, URL)

        if projects:
            generate_pdf(projects)
        else:
            print("Error occurred.")
    else:
        print("Login failed")


if __name__ == '__main__':
    main()
