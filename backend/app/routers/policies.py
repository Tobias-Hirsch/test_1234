from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.database import get_db, Policy, User
from app.schemas import schemas
from app.dependencies.permissions import require_abac_permission, check_permission
from app.services.auth import get_current_active_user
from app.services.query_filter_service import QueryFilterService, get_query_filter_service

router = APIRouter(
    prefix="/policies",
    tags=["policies"],
)

@router.post("", response_model=schemas.Policy, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_abac_permission("policy", "create"))], include_in_schema=False)
@router.post("/", response_model=schemas.Policy, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_abac_permission("policy", "create"))])
def create_policy(policy: schemas.PolicyCreate, db: Session = Depends(get_db)):
    db_policy = Policy(
        name=policy.name,
        description=policy.description,
        actions=policy.actions,
        subjects=policy.subjects,
        resources=policy.resources,
        conditions=policy.conditions,
        is_active=policy.is_active,
        effect=policy.effect
    )
    db.add(db_policy)
    db.commit()
    db.refresh(db_policy)
    return db_policy

@router.get("", response_model=List[schemas.Policy], include_in_schema=False)
@router.get("/", response_model=List[schemas.Policy])
def read_policies(
    db: Session = Depends(get_db),
    qfs: QueryFilterService = Depends(get_query_filter_service),
    skip: int = 0,
    limit: int = 100
):
    """
    Retrieve a list of policies, filtered by the current user's permissions.
    """
    filters = qfs.get_query_filters(resource_type="policy", action="read_list")
    policies = db.query(Policy).filter(*filters).offset(skip).limit(limit).all()
    return policies

@router.get("/{policy_id}", response_model=schemas.Policy)
def read_policy(
    policy_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    policy = db.query(Policy).filter(Policy.id == policy_id).first()
    if policy is None:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    check_permission(db, current_user, "read", resource_obj=policy)
    
    return policy

@router.put("/{policy_id}", response_model=schemas.Policy,
            dependencies=[Depends(require_abac_permission("policy", "update"))])
def update_policy(policy_id: int, policy_update: schemas.PolicyUpdate, db: Session = Depends(get_db)):
    db_policy = db.query(Policy).filter(Policy.id == policy_id).first()
    if db_policy is None:
        raise HTTPException(status_code=404, detail="Policy not found")

    for field, value in policy_update.model_dump(exclude_unset=True).items():
        setattr(db_policy, field, value)

    db.commit()
    db.refresh(db_policy)
    return db_policy

@router.delete("/{policy_id}", status_code=status.HTTP_200_OK,
                dependencies=[Depends(require_abac_permission("policy", "delete"))])
def delete_policy(policy_id: int, db: Session = Depends(get_db)):
    db_policy = db.query(Policy).filter(Policy.id == policy_id).first()
    if db_policy is None:
        raise HTTPException(status_code=404, detail="Policy not found")

    db.delete(db_policy)
    db.commit()
    return {"message": "Policy deleted successfully"}