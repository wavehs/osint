import asyncio
import database
import models
from models import BaseEntity
from modules.domain_transforms import Sublist3rTransform, TheHarvesterTransform
from modules.ip_transforms import NmapTransform, MasscanTransform
from modules.username_transforms import SherlockTransform

class InvestigationEngine:
    def __init__(self, investigation_id: int):
        self.investigation_id = investigation_id
        self.transform_map = {}
        self.register_transforms()

    def register_transforms(self):
        """
        Registers all available transforms and maps them to the entity types they support.
        """
        # This can be made more dynamic later, e.g., by discovering subclasses of BaseTransform
        self.transform_map = {
            "Domain": [Sublist3rTransform, TheHarvesterTransform],
            "IPAddress": [NmapTransform, MasscanTransform],
            "Username": [SherlockTransform],
        }
        print(f"Registered transforms: {self.transform_map}")


    async def start(self, seed_entity: BaseEntity):
        """
        Starts the investigation with a seed entity.
        """
        print(f"Starting investigation {self.investigation_id} with seed {seed_entity.value}")
        await self._main_loop()

    async def _main_loop(self):
        """
        The main processing loop of the engine.
        """
        while True:
            entity_to_process = await database.get_next_queued_entity()
            if not entity_to_process:
                print("No more entities to process. Investigation complete.")
                break

            print(f"Processing entity: {entity_to_process.value} (Type: {entity_to_process.type})")
            await database.set_entity_status(entity_to_process.id, "PROCESSING")
            await self._route_entity(entity_to_process)
            await database.set_entity_status(entity_to_process.id, "DONE")

    async def _route_entity(self, entity: database.Entity):
        """
        Routes an entity to the appropriate transforms based on its type.
        """
        entity_model = self._pydantic_model_from_entity(entity)
        if not entity_model:
            return

        transforms_to_run = self.transform_map.get(entity.type, [])
        if not transforms_to_run:
            print(f"No transforms registered for entity type: {entity.type}")
            return

        tasks = [
            self._run_transform(transform_class(self.investigation_id), entity_model)
            for transform_class in transforms_to_run
        ]
        await asyncio.gather(*tasks, return_exceptions=True) # return_exceptions=True to prevent one failure from stopping all

    def _pydantic_model_from_entity(self, entity: database.Entity) -> BaseEntity | None:
        """
        Dynamically converts a SQLAlchemy Entity object to its corresponding Pydantic model.
        """
        model_class = getattr(models, entity.type, None)
        if model_class and issubclass(model_class, BaseEntity):
            return model_class(value=entity.value)
        else:
            print(f"Warning: No Pydantic model found for entity type {entity.type}")
            return None


    async def _run_transform(self, transform_instance, entity: BaseEntity):
        """
        Executes a single transform instance.
        """
        print(f"Running transform {transform_instance.name} on {entity.value}")
        try:
            raw_output = await transform_instance.run(entity)
            new_entities = transform_instance.parse(raw_output)
            print(f"Transform {transform_instance.name} found {len(new_entities)} new entities.")

            for new_entity in new_entities:
                entity_type = new_entity.__class__.__name__
                await database.add_entity_if_not_exists(
                    self.investigation_id,
                    entity_type,
                    new_entity.value,
                    source=transform_instance.name
                )
        except Exception as e:
            print(f"Transform {transform_instance.name} FAILED on {entity.value}: {e}")
