"""Rigenera i750esempi Web/Backend e Database dalle fonti curate."""
import database_catalog,web_node,web_react,web_next,web_aspnet,web_fastapi,web_html,web_django

def build_all():
    for module in (database_catalog,web_node,web_react,web_next,web_aspnet,web_fastapi,web_html,web_django):
        module.build_all()

if __name__=='__main__':build_all()
