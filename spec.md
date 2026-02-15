# Spec

## Summary

This is a webpage advertising 508.dev's "Interview Service." Users can use the website to find expert engineers offering paid 1 hour practice interviews with 30 minute feedback sessions, schedule a session, and pay for the service.

## Background

508.dev LLC is an engineer-owned co-op with members all around the world. Its primary business model is contracting engineering services, however it's exploring alternative business models to maximize the earning potential of its members. This website is one such venture.

## UX Details

This webpage is broken into several section.

1. Homepage
2. Available Interviewers
3. Booking flow
4. Admin panel

### 1. Homepage

The Homepage is mostly a marketing and explainer page. It explains the service, sells the benefits of using the service, contains testamonials, advertises the companies our members have worked for, and shows a small selection of available interviewers.

### 2. Available Interviewers

This is essentially a "product page." It will list the available interviewers with some basic information about them including a summary of their work history and tags of their interview topics.

Tags are broken into two categories: "technologies" and "interview subjects." Examples of "technologies" include "React," "Typescript," "Python," "C." Examples of "interview subjects" include "Frontend," "Backend," "System Design," "Fullstack," "Machine Learning Engineer." Any given interviewer can have any combination of tags in either category.

The price per interview for a given interviewer will also be shown.

Clicking a user will open a modal with more information about them, as well a button to enter the booking flow.

### 3. Booking Flow

This page will show the availability of the interviewer using a cal.com widget, connected to a custom "Event Type" in cal.com. Upon selection of a date and time, the user will be directed to a payment flow in Stripe. During this flow, our Satisfaction Guarantee will be explained, which is a 100% money back guarantee if they didn't find value in the interview and the feedback provided after.

Here will also be explained the service in detail, which is a one hour technical interview for a specific set of technologies and interview subject (e.g. frontend interview for react, backend interview for Python and FastAPI) followed with by a 30 minute feedback session.

The user will enter customer detials such as name, email, background, and a free text input for what specifically they'd like to be interviewed on. Another optional input asks what companies or stage of companies they're interviewing for, so the interviewer can try to tailor it to that style of company if they can. (e.g. Google and Amazon, or "startups"). There is another free text field asking for any extra information the interviewer should know, and a file attachment section for the user's resume. There is then a payment portal for stripe.

Upon conclusion of payment, a "Thank you" style page is shown indicating that the user should expect an email confirmation should arrive in their inbox immediately, followed up by confirmation from the interviewer that they've received their information.

### 4. Admin Panel

Separate from the main site, an admin panel is available for interviewers. Each interviewer has their own login to their own admin panel.

On the admin panel, an interviewer can see their upcoming interviews, edit the personal details, skills, and interview subjects displayed for them on the user-facing site, and update their rate. For upcoming interviews, the interviewer can see the date and time, as well as any information entered into the form during the billing process.

## Implementation Details

### Unanswered Questions

The following details are as of yet undecided. An LLM viewing these questions should guide the engineer building this app with options for the below questions, record the decision within the implementation details section, and remove questions from the list once a decision has been made.

1. In Django, how can a user attach a pdf during payment flow in such a way that it can be viewed by an interviewer using the admin portal later?

2. How can we send custom confirmation emails from our app after payment concludes?

3. How do we associate each interviewer with their associated cal.com account, and represent that to the app?

4. What's a good way to get dev hot reloading for an HTMX app?

5. In prod, how should the HTMX frontend be served?

6. How should frontend testing be done?

7. How should backend testing be done?

### Decisions

The app is a django / htmx app. CSS is styled without any libraries. Only modern browsers are targeted. A postgresql DB is used.

For development, a docker compose dev file is used to spin up a postgres db, that the django dev app can connect to. The HTMX frontend can be served in some way that allows hot reloading.

For deployment, a docker compose prod version is available that bundles the DB and backend together, as well as builds the frontend. The frontend is then [UNDECIDED].

Any javascript necessary is typescript.

The app will be deployed on push to main via coolify.
