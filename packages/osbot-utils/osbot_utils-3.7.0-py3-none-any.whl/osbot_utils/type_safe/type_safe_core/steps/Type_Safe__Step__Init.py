from typing                                                                     import ForwardRef
from osbot_utils.type_safe.type_safe_core.collections.Type_Safe__Dict           import Type_Safe__Dict
from osbot_utils.type_safe.type_safe_core.collections.Type_Safe__List           import Type_Safe__List
from osbot_utils.type_safe.type_safe_core.collections.Type_Safe__Set            import Type_Safe__Set
from osbot_utils.type_safe.type_safe_core.collections.Type_Safe__Tuple          import Type_Safe__Tuple
from osbot_utils.type_safe.type_safe_core.shared.Type_Safe__Annotations         import type_safe_annotations
from osbot_utils.type_safe.type_safe_core.steps.Type_Safe__Step__Default_Value  import type_safe_step_default_value, get_args


class Type_Safe__Step__Init:

    def init(self, __self         ,
                   __class_kwargs ,
                   **kwargs
              ) -> None:

        for (key, value) in __class_kwargs.items():                             # assign all default values to target
            if hasattr(__self, key):
                existing_value = getattr(__self, key)
                if existing_value is not None:
                    setattr(__self, key, existing_value)
                    continue
            setattr(__self, key, value)

        for (key, value) in kwargs.items():                                     # overwrite with values provided in ctor
            if hasattr(__self, key):
                if value is not None:                                           # prevent None values from overwriting existing values, which is quite common in default constructors
                    value = self.convert_value_to_type_safe_objects(__self, key, value)
                    setattr(__self, key, value)
            else:
                raise ValueError(f"{__self.__class__.__name__} has no attribute '{key}' and cannot be assigned the value '{value}'. "
                                 f"Use {__self.__class__.__name__}.__default_kwargs__() see what attributes are available") from None

    def convert_value_to_type_safe_objects(self, __self, key, value):
        annotation = type_safe_annotations.obj_attribute_annotation(__self, key)
        if annotation:
            enum_type = type_safe_annotations.extract_enum_from_annotation(annotation)
            if enum_type and type(value) is str:                                                                # Apply enum conversion logic
                if value in enum_type.__members__:                                                              # First check if it's a valid name (e.g., 'SYSTEM')
                    value = enum_type[value]
                elif hasattr(enum_type, '_value2member_map_') and value in enum_type._value2member_map_:        # Then check if it's a valid value (e.g., 'system')
                    value = enum_type._value2member_map_[value]
                else:
                    raise ValueError(f"Invalid value '{value}' for enum {enum_type.__name__}")
            else:

                origin = type_safe_annotations.get_origin(annotation)
                # If the value is an empty container, create proper type-safe container
                if ((isinstance(value, list ) and len(value) == 0) or
                    (isinstance(value, dict ) and len(value) == 0) or
                    (isinstance(value, set  ) and len(value) == 0) or
                    (isinstance(value, tuple) and len(value) == 0)):
                    value = type_safe_step_default_value.default_value(__self.__class__, annotation)        # Use default_value to create the proper type-safe container
                            # Handle non-empty list
                elif origin is list and isinstance(value, list):
                    args = get_args(annotation)
                    if args:                                                        # Only create Type_Safe__List if we have type info
                        item_type = args[0]
                        if isinstance(item_type, ForwardRef):
                            forward_name = item_type.__forward_arg__
                            if forward_name == __self.__class__.__name__:
                                item_type = __self.__class__
                        type_safe_list = Type_Safe__List(expected_type=item_type)
                        for item in value:
                            type_safe_list.append(item)
                        return type_safe_list

                # Handle non-empty set
                elif origin is set and isinstance(value, set):
                    args = get_args(annotation)
                    if args:  # Only create Type_Safe__Set if we have type info
                        item_type = args[0]
                        type_safe_set = Type_Safe__Set(expected_type=item_type)
                        for item in value:
                            type_safe_set.add(item)
                        return type_safe_set

                # Handle non-empty tuple
                elif origin is tuple and isinstance(value, tuple):
                    item_types = get_args(annotation)
                    return Type_Safe__Tuple(expected_types=item_types, items=value)

                # Handle non-empty dict
                elif origin is dict and isinstance(value, dict):
                    args = get_args(annotation)
                    if args and len(args) == 2:  # Only create Type_Safe__Dict if we have both key and value types
                        key_type, value_type = args
                        type_safe_dict       = Type_Safe__Dict(expected_key_type=key_type, expected_value_type=value_type)
                        for k, v in value.items():
                            type_safe_dict[k] = v
                        return type_safe_dict


        return value

type_safe_step_init = Type_Safe__Step__Init()