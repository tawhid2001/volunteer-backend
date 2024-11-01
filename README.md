# Volunteer Hub - Backend

**Volunteer Hub** is a web application built using Django and Django REST Framework (DRF) that connects individuals looking to organize volunteer work with those willing to participate. The platform allows users to post about upcoming volunteer opportunities, join initiatives, and provide feedback on their experiences.

## Features

- **User Authentication**: Allows users to register and log in.
- **Volunteer Opportunity Management**: Organizers can create, view, and manage volunteer opportunities.
- **Join Requests**: Users can send join requests to participate in volunteer work.
- **Rating and Review System**: Users can assess the impact of volunteer activities by submitting reviews and ratings.
- **REST API**: Backend endpoints are available for frontend integration.

## Technologies

- **Backend Framework**: Django, Django REST Framework (DRF)
- **Database**: SQLite (default), configurable to PostgreSQL or MySQL
- **Deployment**: Render

## Live Demo

You can access the live backend API here: [Volunteer Hub Live](https://volunteerhub-backend-zlno.onrender.com/)

## Important URLs and Endpoints

### Authentication

- **Login**: `POST /api/auth/login/`
- **Registration**: `POST /api/auth/registration/`

### Volunteer Opportunities

- **Create Volunteer Opportunity**: `POST /api/volunteer/`
- **List Volunteer Opportunities**: `GET /api/volunteer/`
- **Volunteer Opportunity Detail**: `GET /api/volunteer/<int:id>/`

### Join Requests

- **Join Request for Opportunity**: `POST /api/volunteer/<int:id>/join/`
- **List My Join Requests**: `GET /api/my-join-requests/`

### Reviews

- **Submit Review**: `POST /api/volunteer/<int:id>/review/`
- **List Reviews for Opportunity**: `GET /api/volunteer/<int:id>/reviews/`

## Local Setup

To set up the Volunteer Hub backend locally, follow these steps:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/tawhid2001/VolunteerHub_backend.git
   cd VolunteerHub_backend
