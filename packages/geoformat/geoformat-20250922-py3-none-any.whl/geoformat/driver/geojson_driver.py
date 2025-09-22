import json

from geoformat.conf.fields_variable import geoformat_field_type_to_geojson_field_type
from geoformat.conf.format_data import value_to_iterable_value
from geoformat.conf.geoformat_var import GEOLAYER_DEFAULT_NAME
from geoformat.conf.geometry_variable import GEOFORMAT_GEOMETRY_TYPE
from geoformat.conf.path import path_to_file_path
from geoformat.conf.proj_var import proj_correspondance
from geoformat.conversion.feature_conversion import feature_deserialize
from geoformat.conversion.feature_conversion import features_filter
from geoformat.conversion.fields_conversion import recast_field_value
from geoformat.driver.common_driver import _get_recast_field_type_mapping, load_data
from geoformat.manipulation.geolayer_manipulation import feature_list_to_geolayer


def feature_attributes_to_properties(attributes, recast_field_mapping=None):
    """
    Transforms feature's attributes to geojson properties

    :param attributes: feature attributes
    :param recast_field_mapping: config dict to recast field to geojson properties format
    :return: formatted geojson properties
    """
    if attributes:
        # check is data are serialized or not
        properties = dict(attributes)

        # if recast_field_mapping
        if recast_field_mapping is not None:
            for field_name, field_name_mapping in recast_field_mapping.items():
                field_value_to_recast = attributes.get(field_name, None)
                if field_value_to_recast:
                    field_value_recast = recast_field_value(field_value=field_value_to_recast, **field_name_mapping)
                    properties[field_name] = field_value_recast
    else:
        properties = {}

    return properties


def geoformat_feature_to_geojson_feature(feature, i_feat=None, recast_field_mapping=None):
    """
    Make transformation between geoformat feature to geojson feature.

    :param feature: geoformat feature
    :param i_feat: geoformat feature's id
    :param recast_field_mapping:
    :return: dict like geojson feature
    """
    # get geometries
    geometry = dict(feature.get('geometry', {}))
    # delete bbox if exists
    geometry.pop('bbox', None)
    # get attributes and clean it
    attributes = dict(feature.get('attributes', {}))
    properties = feature_attributes_to_properties(attributes, recast_field_mapping)
    geojson_feature = dict(
        type='Feature',
        geometry=geometry,
        properties=properties
    )
    if i_feat is not None:
        geojson_feature['id'] = i_feat

    return geojson_feature




def geolayer_to_geojson(
    geolayer,
    path,
    overwrite=False,
    add_extension=False,
    indent=4,
    encoding='utf8'
):
    """
    Save geolayer to geojson format

    :param geolayer: input geolayer.
    :param path: output geojson file or directory path .
    :param overwrite: True we overwrite if exists false we raise an exception.
    :param add_extension: True we add .geojson extension to file path if extension .geojson not exists.
    :param indent: format output file with specific indentation.
    :param encoding: string encoding default utf8.

    """

    if add_extension:
        add_extension = '.geojson'

    # check input path and deduce output path
    output_path = path_to_file_path(
        path=path,
        geolayer_name=geolayer['metadata']['name'],
        overwrite=overwrite,
        add_extension=add_extension
    )

    # scan field metadata to check if field must have to be recast
    fields_metadata = geolayer['metadata'].get('fields', {})
    recast_field_mapping = _get_recast_field_type_mapping(
        fields_metadata=fields_metadata,
        geoformat_type_to_output_driver_type=geoformat_field_type_to_geojson_field_type
    )

    geojson_features_list = [None] * len(geolayer['features'])
    for i, (i_feat, feature) in enumerate(geolayer['features'].items()):
        if geolayer['metadata'].get('serialize', False):
            feature = feature_deserialize(feature)
        geojson_feature = geoformat_feature_to_geojson_feature(
            feature=feature,
            i_feat=i_feat,
            recast_field_mapping=recast_field_mapping)
        geojson_features_list[i] = geojson_feature

    # create FeatureCollection
    name = geolayer['metadata']['name']
    geojson_feature_collection = {'type': "FeatureCollection", "name": name, "features": geojson_features_list}

    # if reference coordinate system (crs) is filled
    if 'geometry_ref' in geolayer['metadata']:
        if 'crs' in geolayer['metadata']['geometry_ref']:
            geolayer_crs = geolayer['metadata']['geometry_ref']['crs']
            crs_string = {
                "type": "name",
                "properties": {
                    "name": "urn:ogc:def:crs:EPSG::{crs}".format(crs=geolayer_crs)
                }
            }
            crs_string = crs_string
            geojson_feature_collection['crs'] = crs_string

    # write geojson file
    with open(output_path, 'w', encoding=encoding) as geojson_file:
        json.dump(obj=geojson_feature_collection, fp=geojson_file, indent=indent)


# def load_json_data(path, http_headers=None, encoding=None):
#     """
#     Return a tuple that contain : json load to str (index 0) and name of geojson (index 1)
#
#     :param path: json path
#     :param http_headers: for http request we can use optionally headers
#     :return: json load to str (index 0) and name of geojson (index 1)
#     """
#     if path_is_file(path=path):
#         p = verify_input_path_is_file(path=path)
#         # open file
#         with open(p, 'r', encoding=encoding) as geojson_file:
#             json_object = json.loads(geojson_file.read())
#         json_name = p.stem
#     elif path_is_http(path=path, headers=http_headers):
#         p = verify_input_path_is_http(path=path, headers=http_headers)
#         http_req = open_http_path(path=p, headers=http_headers)
#         json_object = json.loads(http_req.read())
#         json_name = http_req.info().get_filename().replace('.json', "").replace('.geojson', '')
#
#     return json_object, json_name


def json_object_to_feature_generator(
        json_object,
):
    """
    Transform geojson FeatureCollection / Feature or Geometry to geoformat Feature

    :param json_object: geojson object transform to python dict
    :return: geoformat feature
    """
    # if it's a Feature Collection
    if json_object["type"] == "FeatureCollection":
        for i_feat, json_feature in enumerate(json_object["features"]):
            for feature in json_object_to_feature_generator(json_feature):
                if feature:
                    yield feature

    # if it's a Feature
    elif json_object["type"] == "Feature":
        feature = {}

        if "properties" in json_object:
            if json_object["properties"]:
                feature["attributes"] = dict(json_object["properties"])

        if "geometry" in json_object:
            if json_object["geometry"]:
                feature["geometry"] = dict(json_object["geometry"])

        if feature:
            yield feature

    # if it's a geometry
    elif json_object["type"].upper() in GEOFORMAT_GEOMETRY_TYPE:
        feature = {"geometry": dict(json_object)}

        if feature:
            yield feature
    else:
        raise Exception("no geojson compatible data")


def from_geojson_get_features_list(
        geojson_in_dict,
        field_name_filter,
        geometry_type_filter,
        bbox_filter,
        serialize,
        bbox_extent,
        feature_limit,
        feature_offset
):
    """
    From geojson transform to dict this function return a features list with some filter option(s)

    :param geojson_in_dict:
    :param field_name_filter:
    :param geometry_type_filter:
    :param bbox_filter:
    :param serialize:
    :param bbox_extent:
    :param feature_limit:
    :param feature_offset:
    :return: list with feature(s) inside
    """
    # create feature generator from file
    features_generator = json_object_to_feature_generator(
        json_object=geojson_in_dict
    )
    # get features list
    features_list = [
        feature for feature in features_filter(
            geolayer_feature_list_or_generator=features_generator,
            field_name_filter=field_name_filter,
            geometry_type_filter=geometry_type_filter,
            bbox_filter=bbox_filter,
            serialize=serialize,
            bbox_extent=bbox_extent,
            feature_limit=feature_limit,
            feature_offset=feature_offset,
        )
    ]

    return features_list


def geojson_to_geolayer(
    path,
    geolayer_name=None,
    field_name_filter=None,
    geometry_type_filter=None,
    bbox_extent=True,
    bbox_filter=None,
    serialize=False,
    feature_limit=None,
    feature_offset=None,
    force_field_conversion=False,
    crs=None,
    http_headers=None,
    encoding="utf8"
):
    """
    Convert geojson file to geolayer

    :param path: path to geojson file
    :param field_name_filter: field_name that we want to keep in geolayer (can be a list).
    :param geometry_type_filter: keep only features with geometry type in this variable (can be a list).
    :param bbox_extent: add "bbox" key in each features and "extent" key in geometry metadata.
    :param bbox_filter: keep only feature that intersects bbox (can be a list of bbox).
    :param serialize: True if features in geolayer are serialized (can reduce performance) / False if not.
    :param feature_limit: constrains the number of rows returned in output geolayer.
    :param feature_offset: skip feature before beginning to given line number.
    :param force_field_conversion:  True if you want to force value in field (can change field type) / False if you want
           to deduce field type without forcing field type.
    :param crs: epsg code for coordinates reference system.
    :param http_headers:
    :param encoding: string encoding default utf8

    :return geolayer: geolayer
    """

    # init and prepare variable
    field_name_filter = value_to_iterable_value(field_name_filter, output_iterable_type=list)
    geometry_type_filter = value_to_iterable_value(geometry_type_filter, output_iterable_type=set)
    bbox_filter = value_to_iterable_value(bbox_filter, output_iterable_type=tuple)

    # load data and get name
    data_geojson_raw, name = load_data(path=path, encoding=encoding, http_headers=http_headers)
    with open(data_geojson_raw.name, 'r') as geojson_data:
        data_geojson_in_dict = json.loads(geojson_data.read())
        geolayer_name = geolayer_name or name or GEOLAYER_DEFAULT_NAME
        if data_geojson_in_dict:
            # filter features
            features_list = from_geojson_get_features_list(
                geojson_in_dict=data_geojson_in_dict,
                field_name_filter=field_name_filter,
                geometry_type_filter=geometry_type_filter,
                bbox_filter=bbox_filter,
                serialize=None,
                bbox_extent=False,
                feature_limit=feature_limit,
                feature_offset=feature_offset
            )

            # create geolayer from filter feature list
            geolayer = feature_list_to_geolayer(
                feature_list=features_list,
                geolayer_name=geolayer_name,
                field_name_filter=None,
                force_field_conversion=force_field_conversion,
                geometry_type_filter=None,
                bbox_filter=None,
                bbox_extent=bbox_extent,
                crs=crs,
                serialize=serialize,
            )

            # add coordinate reference system
            if "crs" in data_geojson_in_dict and crs is None:
                if 'geometry_ref' in geolayer['metadata']:
                    crs_raw_value = data_geojson_in_dict['crs']['properties']['name'].split(':')[-1]
                    try:
                        crs = int(crs_raw_value)
                    except ValueError:
                        crs = proj_correspondance.get(crs_raw_value)

            if crs and 'geometry_ref' in geolayer['metadata']:
                geolayer['metadata']['geometry_ref']['crs'] = crs

        return geolayer
