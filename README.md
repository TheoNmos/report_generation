# report generation and AI helper

#### This project is basically an implementation of a friendly way to query a database, which contains the data retrieved from am AI chatbot.

I decided to use **FastAPI** for this implementation because of its async nature.

---

There was a need to generate some reports monthly using SQL. However, the guys that work for the chatbot startup don't really know how to interact with databases.

So, i decided to create a simple API to help them retrieve and export the data that they want.

---

Also, i created an AI workflow, which creates brand new queries to get the data needed to answer the user question.

After getting the data, some insights are generated based on the results and user prompt.

---

There is a really simple frontend to interact with the AI workflow, but that's not the focus of the app.

The guys will be using the FastAPI swagger to interact with the routes, which i believe it very usefull in scenarios like this, when you're only going to use the tool internally and don't have many routes.
