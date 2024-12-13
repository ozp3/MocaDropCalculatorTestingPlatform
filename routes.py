from flask import render_template, request, redirect, url_for
from services.project_service import fetch_projects, get_pool_data, check_deadline, fetch_token_price
from datetime import datetime

def setup_routes(app):
    @app.route("/", methods=["GET", "POST"])
    def index():
        projects = fetch_projects()

        if not projects:
            return render_template(
                "index.html",
                error="Could not fetch projects from Mocaverse API.",
                projects=[],
                token_name="",
                tokens_offered="",
                total_sp_burnt="",
                registration_end_date="",
                is_ended=False,
                token_price=None,
            )

        selected_project_name = request.form.get("project") or projects[0]["name"]
        selected_project = next((p for p in projects if p["name"] == selected_project_name), None)

        if not selected_project:
            return render_template(
                "index.html",
                error="Invalid project selected.",
                projects=projects,
                token_name="",
                tokens_offered="",
                total_sp_burnt="",
                registration_end_date="",
                is_ended=False,
                token_price=None,
            )

        total_sp_burnt, registration_end_date = get_pool_data(selected_project["url"])
        if total_sp_burnt is None:
            return render_template(
                "index.html",
                error="Could not fetch Total SP Burnt from Mocaverse API.",
                projects=projects,
                token_name=selected_project["name"],
                tokens_offered="Error fetching data",
                total_sp_burnt="Error fetching data",
                registration_end_date=registration_end_date,
                is_ended=False,
                token_price=None,
            )

        # Test için "ongoing" zorlaması
        # is_ended = check_deadline(selected_project["registrationEndDate"])
        is_ended = False  # Proje her zaman ongoing olarak kabul ediliyor

        token_price = None
        if not is_ended and selected_project["tokenTicker"]:
            token_price = fetch_token_price(selected_project["tokenTicker"])

        return render_template(
            "index.html",
            projects=projects,
            token_name=selected_project["name"],
            tokens_offered=f"{float(selected_project['tokensOffered']):,.0f}",
            total_sp_burnt=f"{total_sp_burnt:,.0f}",
            registration_end_date=registration_end_date,
            is_ended=is_ended,
            token_price=token_price,
        )

    @app.route("/result")
    def result():
        return render_template(
            "result.html",
            token_name=request.args.get("token_name"),
            tokens_offered=request.args.get("tokens_offered"),
            total_sp_burnt=request.args.get("total_sp_burnt"),
            token_price=request.args.get("token_price"),
            your_sp_burn=request.args.get("your_sp_burn"),
            reward=request.args.get("reward"),
            tokens_received=request.args.get("tokens_received"),
        )
