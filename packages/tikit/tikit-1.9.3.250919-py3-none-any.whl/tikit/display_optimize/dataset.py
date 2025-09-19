# -*- coding: utf-8 -*-
from prettytable import PrettyTable

from tikit.tencentcloud.tione.v20211111 import models


def dataset_table(dataset_response):
    """

    :param dataset_response:
    :type dataset_response:   :class:`tikit.tencentcloud.tione.v20211111.models.DescribeDatasetsResponse`
    :return:
    :rtype:
    """
    type_dict = {
        "TYPE_DATASET_TEXT": "文本",
        "TYPE_DATASET_TABLE": "表格",
        "TYPE_DATASET_IMAGE": "图片",
        "TYPE_DATASET_OTHER": "其他",
    }
    unit_dict = {
        "TYPE_DATASET_TEXT": "行",
        "TYPE_DATASET_TABLE": "行",
        "TYPE_DATASET_IMAGE": "张",
        "TYPE_DATASET_OTHER": "个",
        "": ""
    }
    table = PrettyTable()
    table.field_names = [
        "ID",
        "名称",
        "版本",
        "类型",
        "标签",
        "状态",
        "数据量",
        "数据集路径",
        "标签存储路径",
        "标注任务名称",
        "创建时间"
    ]

    for dataset in dataset_response.DatasetGroups:
        dataset_type = dataset.DatasetScene
        if dataset.DatasetType in type_dict:
            dataset_type = type_dict[dataset.DatasetType]
        if dataset.DatasetScene == "LLM":
            if dataset.AnnotationType == "ANNOTATION_TYPE_MLLM":
                dataset_type = "大模型建模-MLLM"
            elif dataset.AnnotationType == "ANNOTATION_TYPE_LLM":
                dataset_type = "大模型建模-LLM"

        data_path = "COS:" + str(dataset.StorageDataPath)
        if dataset.DataSourceConfig is not None and dataset.DataSourceConfig.DataSourceId is not None and dataset.DataSourceConfig.DataSourceId != "":
            data_path = "数据源:" + str(dataset.DataSourceConfig)
        elif dataset.CFSConfig is not None and dataset.CFSConfig.Id is not None and dataset.CFSConfig.Id != "":
            data_path = "CFS:" + str(dataset.CFSConfig)

        label_path = ""
        if dataset.StorageLabelPath is not None and dataset.StorageLabelPath.Bucket is not None and dataset.StorageLabelPath.Bucket != "":
            label_path = str(dataset.StorageLabelPath)

        table.add_row([
            dataset.DatasetId,
            dataset.DatasetName,
            dataset.DatasetVersion,
            dataset_type,
            "\n".join(map(lambda x: "%s:%s" % (x.TagKey, x.TagValue), dataset.DatasetTags)),
            dataset.DatasetStatus,
            "{}{}".format(dataset.FileNum, unit_dict[dataset.DatasetType]),
            data_path,
            label_path,
            dataset.DatasetAnnotationTaskName,
            dataset.CreateTime
        ])
    return table


def dataset_str(self):
    return dataset_table(self).get_string()


def dataset_html(self):
    return dataset_table(self).get_html_string()


def detail_structured_table(detail_structured):
    """

    :param detail_structured:
    :type detail_structured:   :class:`tikit.tencentcloud.tione.v20211111.models.DescribeDatasetDetailStructuredResponse`
    :return:
    :rtype:
    """
    table = PrettyTable()
    table.field_names = detail_structured.ColumnNames
    for row_item in detail_structured.RowItems:
        row = []
        for column in table.field_names:
            field_value = ""
            for name_value in row_item.Values:
                if name_value.Name == column:
                    field_value = name_value.Value
                    break
            row.append(field_value)
        table.add_row(row)
    return table


def detail_structured_str(self):
    return detail_structured_table(self).get_string()


def detail_structured_html(self):
    return detail_structured_table(self).get_html_string()


def detail_unstructured_table(detail_unstructured):
    """

    :param detail_unstructured:
    :type detail_unstructured:   :class:`tikit.tencentcloud.tione.v20211111.models.DescribeDatasetDetailStructuredResponse`
    :return:
    :rtype:
    """
    table = PrettyTable()
    table.field_names = [
        "总量",
        "未标注",
        "已标注",
    ]
    table.add_row([
        detail_unstructured.FilterTotalCount,
        detail_unstructured.NonAnnotatedTotalCount,
        detail_unstructured.AnnotatedTotalCount
    ])
    return table


def detail_unstructured_str(self):
    return detail_unstructured_table(self).get_string()


def detail_unstructured_html(self):
    return detail_unstructured_table(self).get_html_string()


models.DescribeDatasetsResponse.__repr__ = dataset_str
models.DescribeDatasetsResponse._repr_html_ = dataset_html

models.DescribeDatasetDetailStructuredResponse.__repr__ = detail_structured_str
models.DescribeDatasetDetailStructuredResponse._repr_html_ = detail_structured_html

models.DescribeDatasetDetailUnstructuredResponse.__repr__ = detail_unstructured_str
models.DescribeDatasetDetailUnstructuredResponse._repr_html_ = detail_unstructured_html
