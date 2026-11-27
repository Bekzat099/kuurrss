# API спецификациясы және Рөлдер матрицасы (6, 9, 10-сабақтар)

Барлық endpoint жолдары `/api/...` префиксімен басталады. Аутентификация **Keycloak (OIDC, RS256 Bearer JWT)** арқылы жүзеге асады.

---

## 1. Endpoint-тер тізімі

| Әдіс | Endpoint жолы | Рөлдер | Сипаттамасы | Статус кодтары |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/health` | Барлығы | Сервердің жұмыс күйін тексеру. | `200` |
| `GET` | `/api/auth/me` | `student`, `teacher`, `admin` | Ағымдағы авторизацияланған пайдаланушы профилін алу (алғаш кіргенде БД-мен синхрондалады). | `200`, `401`, `403`, `503` |
| `GET` | `/api/users` | `admin` | Жүйедегі барлық пайдаланушылар тізімін көру. | `200`, `401`, `403` |
| `GET` | `/api/users/{id}` | `admin` | Нақты пайдаланушыны ID бойынша көру. | `200`, `401`, `403`, `404` |
| `DELETE` | `/api/users/{id}` | `admin` | Пайдаланушыны өшіру (әкімші өзін-өзі өшіре алмайды → `400`). | `204`, `400`, `401`, `403`, `404` |
| `GET` | `/api/quizzes` | Барлығы / Авторизацияланған | Тесттер тізімін алу. | `200` |
| `POST` | `/api/quizzes` | `teacher`, `admin` | Сабақ мәтінінен жаңа тест құрастыру (`draft` күйінде). | `201`, `401`, `403`, `422` |
| `GET` | `/api/quizzes/{id}` | Барлығы / Авторизацияланған | Нақты тестті алу. | `200`, `404` |
| `PATCH` | `/api/quizzes/{id}` | `teacher` (тек өз тесті), `admin` | Тест атауын өзгерту немесе күйін `published` етіп жариялау. | `200`, `401`, `403`, `404`, `422` |
| `DELETE` | `/api/quizzes/{id}` | `teacher` (тек өз тесті), `admin` | Тестті базадан өшіру. | `204`, `401`, `403`, `404` |
| `POST` | `/api/quizzes/{id}/questions` | `teacher` (тек өз тесті), `admin` | Тестке жаңа сұрақ қосу (тек `draft` күйінде және 4 бірегей нұсқамен → әйтпесе `400`). | `201`, `400`, `401`, `403`, `404`, `422` |
| `PATCH` | `/api/questions/{id}` | `teacher` (тек өз тесті), `admin` | Тест ішіндегі сұрақты өңдеу (тек `draft` күйінде → әйтпесе `400`). | `200`, `400`, `401`, `403`, `404`, `422` |
| `DELETE` | `/api/questions/{id}` | `teacher` (тек өз тесті), `admin` | Тест ішіндегі сұрақты өшіру (тек `draft` күйінде → әйтпесе `400`). | `204`, `400`, `401`, `403`, `404` |
| `POST` | `/api/quizzes/{id}/submissions` | `student`, `teacher`, `admin` | Жарияланған тестті тапсыру және автоматты ұпай (`score`) есептеу (`draft` болса → `400`, қайта тапсырса → `409`). | `201`, `400`, `401`, `403`, `404`, `409`, `422` |
| `POST` | `/api/submissions` | `student`, `teacher`, `admin` | Жарияланған тестті тапсыру (денесінде `quiz_id` көрсетіледі). | `201`, `400`, `401`, `403`, `404`, `409`, `422` |
| `GET` | `/api/submissions/me` | `student`, `teacher`, `admin` | Ағымдағы пайдаланушының өз тапсырған тест нәтижелерін алу. | `200`, `401`, `403` |
| `GET` | `/api/submissions` | `teacher`, `admin` | Барлық оқушылардың тапсырған тест нәтижелерін (`?quiz_id={id}`) алу. | `200`, `401`, `403` |

---

## 2. Рөлдер матрицасы (Role Access Matrix — 10-сабақ)

| Endpoint | Аноним (токенсіз) | `student` | `teacher` | `admin` |
| :--- | :---: | :---: | :---: | :---: |
| `GET /api/health` | `200` | `200` | `200` | `200` |
| `GET /api/auth/me` | `401` | `200` | `200` | `200` |
| `GET /api/users` | `401` | `403` | `403` | `200` |
| `GET /api/users/{id}` | `401` | `403` | `403` | `200` |
| `DELETE /api/users/{id}` | `401` | `403` | `403` | `204` (өзін → `400`) |
| `GET /api/quizzes` | `200` | `200` | `200` | `200` |
| `POST /api/quizzes` | `401` | `403` | `201` | `201` |
| `GET /api/quizzes/{id}` | `200` | `200` | `200` | `200` |
| `PATCH /api/quizzes/{id}` | `401` | `403` | `200` (тек өзінікі, бөтен → `403`) | `200` |
| `DELETE /api/quizzes/{id}` | `401` | `403` | `204` (тек өзінікі, бөтен → `403`) | `204` |
| `POST /api/quizzes/{id}/questions` | `401` | `403` | `201` (тек өзінікі, бөтен → `403`) | `201` |
| `PATCH /api/questions/{id}` | `401` | `403` | `200` (тек өзінікі, бөтен → `403`) | `200` |
| `DELETE /api/questions/{id}` | `401` | `403` | `204` (тек өзінікі, бөтен → `403`) | `204` |
| `POST /api/quizzes/{id}/submissions` | `401` | `201` | `201` | `201` |
| `GET /api/submissions/me` | `401` | `200` | `200` | `200` |
| `GET /api/submissions` | `401` | `403` | `200` | `200` |

---

## 3. Сәйкестік кестесі (User Stories ↔ Endpoints ↔ Кестелер)

| Story ID | Endpoint | Кесте атауы |
| :--- | :--- | :--- |
| **US-1** (Must) | `POST /api/quizzes`, `POST /api/quizzes/{id}/questions` | `quizzes`, `questions`, `users` |
| **US-2** (Must) | `PATCH /api/questions/{id}`, `DELETE /api/questions/{id}`, `PATCH /api/quizzes/{id}` | `questions`, `quizzes` |
| **US-3** (Must) | `GET /api/quizzes/{id}`, `POST /api/quizzes/{id}/submissions` | `quizzes`, `questions`, `submissions`, `users` |
| **US-4** (Must) | `GET /api/submissions` | `submissions`, `users`, `quizzes` |
| **US-5** (Should) | `GET /api/users`, `DELETE /api/users/{id}`, `DELETE /api/quizzes/{id}` | `users`, `quizzes`, `questions`, `submissions` |
| **US-6** (Could) | `GET /api/submissions/me` | `submissions`, `quizzes` |
