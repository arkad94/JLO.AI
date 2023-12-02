# JLO.AI
### Consolidated System Design for J.LO.AI v0.01

**Core Components:**
1. User: The app's end-user, engaging with the system to learn Japanese.
2. Filter: The module responsible for filtering input and output, ensuring relevancy to the app's Japanese learning objectives.
3. Admin: The backend component that manages the app's database, tracking and logging changes.
4. Prompter: The interface to the OpenAI API, crafting standardized prompts based on user requests and app requirements.

Functional Scenarios:


Situation 1: User Request Event
- The User initiates a request for learning content or information.
- The Filter evaluates the request. If relevant, it directs the request to the Prompter for OpenAI API interaction or to the Admin for database-related queries.
- The Prompter standardizes the request into a prompt according to pre-set rules and sends this standardized prompt to the OpenAI API. The response from OpenAI is sent directly to the Filter without pre-checks by the Prompter.
- The Admin responds to requests from the Filter about database management and report generation.


Situation 2: API Reply Event
- The OpenAI API sends a response back to the Prompter.
- The Prompter forwards this response directly to the Filter without standardization post-response.
- The Filter performs any necessary checks against the database content with the Admin's assistance, ensuring no duplication, particularly for the 'Word of the Day' feature.
- The Filter handles the storage of incomplete tests and the processing of quiz answers, communicating with the OpenAI API for results.



Situation 3: Database Change Report
- The Admin logs all database changes, including the addition of new words, the status of tests, changes in tags, and maintains a tag cloud.
- The User can request a report on database changes. The Filter facilitates this by retrieving the logged information from the Admin and presenting it to the User.
- Database changes are comprehensive, covering new additions, updates, and the overall landscape of the database's content.

Interaction Flow:
- User ↔ Filter: Direct communication channel for user inputs and receiving responses, learning materials, or reports.
- Filter ↔ Prompter ↔ OpenAI API**: A loop that ensures the OpenAI API receives standardized prompts and provides relevant responses.
- Filter ↔ Admin ↔ Database**: A route for database management, content verification, and change logging.

This system design outlines a structured approach to creating an educational app focused on Japanese language learning. It incorporates a blend of user interaction, content filtering, standardized communication with an AI service, and robust database management to create an environment conducive to learning and growth. 

The design is modular and allows for future expansions or modifications as the app evolves and user needs become more sophisticated.
![Uploading image.png…]()

