// TODO: i18n - processed
/**
 * ReportCanvas Component
 * 
 * The main canvas where fields are dropped and arranged to build the report
 */

import React, { useState, useCallback } from 'react';
import { useDrop } from 'react-dnd';
import { Card, CardContent, CardHeader, CardTitle } from '../../../components/ui/card';
import { Button } from '../../../components/ui/button';
import { Input } from '../../../components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../../components/ui/select';
import { Badge } from '../../../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../../components/ui/tabs';
import {
  DragDropContext,
  Droppable,
  Draggable } from
'react-beautiful-dnd';
import {
  GripVertical,
  X,
  Settings,
  Plus,
  ArrowUp,
  ArrowDown,
  Filter,
  Group,
  SortAsc,
  Table,
  BarChart3,
  Eye } from
'lucide-react';

import FieldDropZone from './dragdrop/FieldDropZone';
import FieldConfigPanel from './FieldConfigPanel';
import GroupingPanel from './GroupingPanel';
import SortingPanel from './SortingPanel';import { useTranslation } from "react-i18next";

const ReportCanvas = ({
  fields = [],
  onFieldDrop,
  onFieldRemove,
  onFieldUpdate,
  onGroupingUpdate,
  onSortingUpdate,
  readonly = false
}) => {const { t } = useTranslation();
  const [selectedField, setSelectedField] = useState(null);
  const [activeTab, setActiveTab] = useState('fields');
  const [layoutMode, setLayoutMode] = useState('table'); // table, chart, custom

  // Drop zone for new fields
  const [{ isOver, canDrop }, drop] = useDrop({
    accept: 'field',
    drop: (item, monitor) => {
      if (monitor.didDrop()) return; // Already handled by a nested drop zone

      // Add to end of fields list
      onFieldDrop(item, fields.length);
    },
    collect: (monitor) => ({
      isOver: monitor.isOver({ shallow: true }),
      canDrop: monitor.canDrop()
    })
  });

  const handleFieldReorder = useCallback((result) => {
    if (!result.destination) return;

    const newFields = Array.from(fields);
    const [reorderedField] = newFields.splice(result.source.index, 1);
    newFields.splice(result.destination.index, 0, reorderedField);

    // Update fields with new order
    newFields.forEach((field, index) => {
      if (field.order !== index) {
        onFieldUpdate(field.id, { order: index });
      }
    });
  }, [fields, onFieldUpdate]);

  const handleFieldSelect = (field) => {
    setSelectedField(field);
  };

  const handleFieldConfigUpdate = (fieldId, updates) => {
    onFieldUpdate(fieldId, updates);

    // Update selected field if it's the one being updated
    if (selectedField && selectedField.id === fieldId) {
      setSelectedField({ ...selectedField, ...updates });
    }
  };

  const getFieldIcon = (field) => {
    switch (field.type) {
      case 'number':
      case 'percentage':
      case 'currency':
        return <BarChart3 className="h-4 w-4" />;
      case 'date':
      case 'datetime':
        return <span className="text-xs font-mono">📅</span>;
      case 'boolean':
        return <span className="text-xs font-mono">☑</span>;
      default:
        return <span className="text-xs font-mono">📝</span>;
    }
  };

  const renderFieldsList = () =>
  <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium">{t("reporting.report_fields")}</h3>
        <div className="flex items-center space-x-2">
          <Select value={layoutMode} onValueChange={setLayoutMode}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="table">
                <div className="flex items-center space-x-2">
                  <Table className="h-4 w-4" />
                  <span>{t("components.table")}</span>
                </div>
              </SelectItem>
              <SelectItem value="chart">
                <div className="flex items-center space-x-2">
                  <BarChart3 className="h-4 w-4" />
                  <span>{t("components.chart")}</span>
                </div>
              </SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Drop Zone */}
      <div
      ref={drop}
      className={`
          min-h-32 border-2 border-dashed rounded-lg p-4 transition-colors
          ${canDrop && isOver ? 'border-blue-500 bg-blue-50' : 'border-gray-300'}
          ${fields.length === 0 ? 'flex items-center justify-center' : ''}
        `}>

        {fields.length === 0 ?
      <div className="text-center text-gray-500">
            <Plus className="h-8 w-8 mx-auto mb-2 text-gray-400" />
            <p className="text-sm">{t("reporting.drag_fields_from_the_palette_to_build_your_report")}

        </p>
            <p className="text-xs text-gray-400 mt-1">{t("reporting.you_can_also_drag_to_reorder_existing_fields")}

        </p>
          </div> :

      <DragDropContext onDragEnd={handleFieldReorder}>
            <Droppable droppableId="fields">
              {(provided, snapshot) =>
          <div
            {...provided.droppableProps}
            ref={provided.innerRef}
            className={`space-y-2 ${snapshot.isDraggingOver ? 'bg-blue-50 rounded-lg p-2' : ''}`}>

                  {fields.map((field, index) =>
            <Draggable
              key={field.id}
              draggableId={field.id}
              index={index}
              isDragDisabled={readonly}>

                      {(provided, snapshot) =>
              <div
                ref={provided.innerRef}
                {...provided.draggableProps}
                className={`
                            bg-white border rounded-lg p-3 transition-all
                            ${snapshot.isDragging ? 'shadow-lg rotate-1' : 'hover:shadow-md'}
                            ${selectedField?.id === field.id ? 'ring-2 ring-blue-500' : ''}
                          `}>

                          <div className="flex items-center space-x-3">
                            {!readonly &&
                  <div
                    {...provided.dragHandleProps}
                    className="cursor-grab hover:cursor-grabbing text-gray-400">

                                <GripVertical className="h-4 w-4" />
                              </div>
                  }

                            <div className="flex-shrink-0">
                              {getFieldIcon(field)}
                            </div>

                            <div className="flex-1 min-w-0">
                              <div className="flex items-center space-x-2">
                                <p className="text-sm font-medium text-gray-900 truncate">
                                  {field.alias || field.name || field.field}
                                </p>
                                <Badge variant="outline" className="text-xs">
                                  {field.type}
                                </Badge>
                                {field.aggregation &&
                      <Badge variant="secondary" className="text-xs">
                                    {field.aggregation}
                                  </Badge>
                      }
                              </div>
                              <p className="text-xs text-gray-500 truncate">
                                {field.source}.{field.field}
                              </p>
                            </div>

                            <div className="flex items-center space-x-1">
                              <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleFieldSelect(field)}
                      className="h-8 w-8 p-0">

                                <Settings className="h-4 w-4" />
                              </Button>
                              
                              {!readonly &&
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => onFieldRemove(field.id)}
                      className="h-8 w-8 p-0 text-red-500 hover:text-red-700">

                                  <X className="h-4 w-4" />
                                </Button>
                    }
                            </div>
                          </div>

                          {/* Field Configuration Preview */}
                          {field.alias !== field.name &&
                <div className="mt-2 text-xs text-blue-600">{t("reporting.display_as")}
                  {field.alias}
                            </div>
                }
                          
                          {field.format &&
                <div className="mt-1 text-xs text-green-600">
                              Format: {field.format}
                            </div>
                }
                        </div>
              }
                    </Draggable>
            )}
                  {provided.placeholder}
                </div>
          }
            </Droppable>
          </DragDropContext>
      }
      </div>

      {/* Field Configuration Panel */}
      {selectedField &&
    <Card>
          <CardHeader>
            <CardTitle className="text-sm">
              Configure: {selectedField.alias || selectedField.name}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <FieldConfigPanel
          field={selectedField}
          onUpdate={(updates) => handleFieldConfigUpdate(selectedField.id, updates)}
          onClose={() => setSelectedField(null)}
          readonly={readonly} />

          </CardContent>
        </Card>
    }
    </div>;


  const renderLayoutPreview = () =>
  <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium">{t("reporting.layout_preview")}</h3>
        <Badge variant="outline">{layoutMode}</Badge>
      </div>

      {fields.length === 0 ?
    <div className="text-center text-gray-500 py-8">
          <Eye className="h-8 w-8 mx-auto mb-2 text-gray-400" />
          <p>{t("reporting.add_fields_to_see_the_layout_preview")}</p>
        </div> :

    <div className="border rounded-lg p-4">
          {layoutMode === 'table' ?
      <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    {fields.map((field) =>
              <th key={field.id} className="text-left p-2 font-medium">
                        {field.alias || field.name}
                      </th>
              )}
                  </tr>
                </thead>
                <tbody>
                  <tr className="border-b text-gray-500">
                    {fields.map((field) =>
              <td key={field.id} className="p-2">
                        {field.type === 'number' ? '123' :
                field.type === 'date' ? '2024-01-01' :
                field.type === 'boolean' ? 'Yes' : 'Sample data'}
                      </td>
              )}
                  </tr>
                  <tr className="text-gray-500">
                    {fields.map((field) =>
              <td key={field.id} className="p-2">
                        {field.type === 'number' ? '456' :
                field.type === 'date' ? '2024-01-02' :
                field.type === 'boolean' ? 'No' : 'More data'}
                      </td>
              )}
                  </tr>
                </tbody>
              </table>
            </div> :

      <div className="text-center text-gray-500 py-8">
              <BarChart3 className="h-8 w-8 mx-auto mb-2" />
              <p>{t("reporting.chart_preview_will_be_available_after_adding_data")}</p>
            </div>
      }
        </div>
    }
    </div>;


  return (
    <div className="h-full flex flex-col">
      <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="fields" className="flex items-center space-x-2">
            <Table className="h-4 w-4" />
            <span>{t("reporting.fields")}</span>
          </TabsTrigger>
          <TabsTrigger value="grouping" className="flex items-center space-x-2">
            <Group className="h-4 w-4" />
            <span>{t("components.grouping")}</span>
          </TabsTrigger>
          <TabsTrigger value="sorting" className="flex items-center space-x-2">
            <SortAsc className="h-4 w-4" />
            <span>{t("reporting.sorting")}</span>
          </TabsTrigger>
          <TabsTrigger value="preview" className="flex items-center space-x-2">
            <Eye className="h-4 w-4" />
            <span>{t("components.preview")}</span>
          </TabsTrigger>
        </TabsList>

        <TabsContent value="fields" className="flex-1 p-4">
          {renderFieldsList()}
        </TabsContent>

        <TabsContent value="grouping" className="flex-1 p-4">
          <GroupingPanel
            fields={fields}
            onGroupingUpdate={onGroupingUpdate}
            readonly={readonly} />

        </TabsContent>

        <TabsContent value="sorting" className="flex-1 p-4">
          <SortingPanel
            fields={fields}
            onSortingUpdate={onSortingUpdate}
            readonly={readonly} />

        </TabsContent>

        <TabsContent value="preview" className="flex-1 p-4">
          {renderLayoutPreview()}
        </TabsContent>
      </Tabs>
    </div>);

};

export default ReportCanvas;