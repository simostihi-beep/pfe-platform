"""Service métier pour la gestion des projets PFE."""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.project import Project, ProjectStatus
from app.models.user import User, UserRole
from app.schemas.project import ProjectCreate, ProjectStatusUpdate, ProjectUpdate


class ProjectService:
    @staticmethod
    def create_project(
        db: Session, project_in: ProjectCreate, student: User
    ) -> Project:
        """Création d'un sujet PFE par un étudiant (statut initial: DRAFT)."""
        if student.role != UserRole.STUDENT:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Seuls les étudiants peuvent déposer un sujet PFE",
            )

        project = Project(
            title=project_in.title,
            description=project_in.description,
            company=project_in.company,
            status=ProjectStatus.DRAFT,
            student_id=student.id,
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def get_project_by_id(db: Session, project_id: int) -> Project:
        """Récupère un projet ou lève 404."""
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Projet introuvable",
            )
        return project

    @staticmethod
    def list_projects_for_user(
        db: Session,
        current_user: User,
        status_filter: ProjectStatus | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Project]:
        """
        Liste les projets selon le rôle :
        - ÉTUDIANT : voit uniquement ses propres sujets.
        - ENSEIGNANT : voit les sujets soumis/validés ou assignés.
        - ADMIN : voit l'ensemble des sujets.
        """
        query = db.query(Project)

        if current_user.role == UserRole.STUDENT:
            query = query.filter(Project.student_id == current_user.id)
        elif current_user.role == UserRole.SUPERVISOR:
            # Un superviseur peut voir tous les sujets soumis, ou ceux qu'il encadre
            query = query.filter(
                (Project.status != ProjectStatus.DRAFT)
                | (Project.supervisor_id == current_user.id)
            )

        if status_filter:
            query = query.filter(Project.status == status_filter)

        return query.order_by(Project.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def update_project(
        db: Session, project_id: int, project_in: ProjectUpdate, current_user: User
    ) -> Project:
        """
        Mise à jour d'un projet :
        - Seul l'étudiant propriétaire peut modifier tant que le statut est DRAFT ou REJECTED.
        - Les admins peuvent toujours modifier.
        """
        project = ProjectService.get_project_by_id(db, project_id)

        if current_user.role != UserRole.ADMIN:
            if project.student_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Vous n'êtes pas autorisé à modifier ce projet",
                )
            if project.status not in [ProjectStatus.DRAFT, ProjectStatus.REJECTED]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Impossible de modifier un projet au statut {project.status.value}",
                )

        update_data = project_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)

        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def update_project_status(
        db: Session,
        project_id: int,
        status_in: ProjectStatusUpdate,
        current_user: User,
    ) -> Project:
        """
        Transition d'états :
        - DRAFT -> SUBMITTED : étudiant propriétaire.
        - SUBMITTED -> VALIDATED : professeur ou admin.
        - SUBMITTED -> REJECTED : professeur ou admin (avec commentaire obligatoire).
        """
        project = ProjectService.get_project_by_id(db, project_id)
        target_status = status_in.status

        if target_status == ProjectStatus.SUBMITTED:
            # L'étudiant soumet son sujet
            if (
                project.student_id != current_user.id
                and current_user.role != UserRole.ADMIN
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Seul l'étudiant titulaire peut soumettre ce projet",
                )
            if project.status not in [ProjectStatus.DRAFT, ProjectStatus.REJECTED]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Impossible de soumettre un projet au statut {project.status.value}",
                )
            project.status = ProjectStatus.SUBMITTED

        elif target_status in [ProjectStatus.VALIDATED, ProjectStatus.REJECTED]:
            # Seul encadrant ou admin peut valider ou refuser
            if current_user.role not in [UserRole.SUPERVISOR, UserRole.ADMIN]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Seuls les encadrants ou administrateurs peuvent valider ou refuser un sujet",
                )
            if (
                project.status != ProjectStatus.SUBMITTED
                and current_user.role != UserRole.ADMIN
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Seul un projet soumis peut être validé ou refusé",
                )

            if target_status == ProjectStatus.REJECTED and not status_in.comment:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Un motif/commentaire est obligatoire lors du refus d'un sujet",
                )

            project.status = target_status
            if (
                current_user.role == UserRole.SUPERVISOR
                and target_status == ProjectStatus.VALIDATED
            ):
                # Si non encore assigné, l'encadrant validant devient l'encadrant du projet
                if not project.supervisor_id:
                    project.supervisor_id = current_user.id
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Transition vers le statut {target_status.value} non supportée",
            )

        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def assign_supervisor(
        db: Session, project_id: int, supervisor_id: int, current_user: User
    ) -> Project:
        """Affectation d'un encadrant (Admin uniquement)."""
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Seul un administrateur peut affecter un encadrant",
            )

        project = ProjectService.get_project_by_id(db, project_id)
        supervisor = db.query(User).filter(User.id == supervisor_id).first()

        if not supervisor or supervisor.role != UserRole.SUPERVISOR:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="L'enseignant encadrant spécifié est introuvable",
            )

        project.supervisor_id = supervisor.id
        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def delete_project(db: Session, project_id: int, current_user: User) -> None:
        """Suppression d'un projet (étudiant si DRAFT, ou ADMIN)."""
        project = ProjectService.get_project_by_id(db, project_id)

        if current_user.role != UserRole.ADMIN:
            if project.student_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Non autorisé à supprimer ce projet",
                )
            if project.status != ProjectStatus.DRAFT:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Seuls les projets au statut brouillon peuvent être supprimés",
                )

        db.delete(project)
        db.commit()
