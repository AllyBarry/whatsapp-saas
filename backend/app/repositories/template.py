"""Template repository."""
from app.models.template import Template
from app.repositories.base import TenantScopedRepository


class TemplateRepository(TenantScopedRepository[Template]):
    model = Template

    def get_by_meta_id(self, meta_template_id: str) -> Template | None:
        stmt = self._scoped().where(Template.meta_template_id == meta_template_id)
        return self.db.scalars(stmt).first()

    def get_by_name(self, name: str, language: str) -> Template | None:
        stmt = self._scoped().where(
            Template.name == name, Template.language == language
        )
        return self.db.scalars(stmt).first()
