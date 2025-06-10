// TODO: i18n - processed
import React, { useState } from 'react';
import { Droppable, Draggable } from '@hello-pangea/dnd';
import {
  GripVertical,
  Settings,
  Copy,
  Trash2,
  ChevronDown,
  ChevronUp,
  Plus,
  Edit2,
  Check,
  X,
  Columns,
  Square,
  Grid3x3 } from
'lucide-react';
import { Card, CardContent, CardHeader } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger } from
'../ui/dropdown-menu';
import ReportWidget from './ReportWidget';import { useTranslation } from "react-i18next";
const ReportSection = ({
  section,
  darkMode,
  isSelected,
  onSelect,
  onUpdate,
  onDelete,
  onDuplicate,
  onUpdateWidget,
  onDeleteWidget,
  dragHandleProps,
  isDragging
}) => {const { t } = useTranslation();
  const [isEditingTitle, setIsEditingTitle] = useState(false);
  const [editedTitle, setEditedTitle] = useState(section.title);
  const [isCollapsed, setIsCollapsed] = useState(false);
  const handleTitleSave = () => {
    onUpdate({ title: editedTitle });
    setIsEditingTitle(false);
  };
  const handleTitleCancel = () => {
    setEditedTitle(section.title);
    setIsEditingTitle(false);
  };
  const getLayoutClass = () => {
    switch (section.layout) {
      case 'two-column':
        return 'grid grid-cols-1 md:grid-cols-2 gap-4';
      case 'grid':
        return 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4';
      default:
        return 'space-y-4';
    }
  };
  const getLayoutIcon = () => {
    switch (section.layout) {
      case 'two-column':
        return <Columns className="w-4 h-4" />;
      case 'grid':
        return <Grid3x3 className="w-4 h-4" />;
      default:
        return <Square className="w-4 h-4" />;
    }
  };
  return (
    <Card
      className={`
        transition-all duration-200
        ${isDragging ? 'shadow-xl scale-[1.02] opacity-90' : ''}
        ${isSelected ? 'ring-2 ring-blue-500' : ''}
        ${darkMode ? 'bg-gray-800 border-gray-700' : 'bg-white'}
      `}
      onClick={() => onSelect()}>

      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3 flex-1">
            {/* Drag Handle */}
            <div
              {...dragHandleProps}
              className="cursor-move p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded">

              <GripVertical className="w-5 h-5 text-gray-400" />
            </div>
            {/* Section Title */}
            {isEditingTitle ?
            <div className="flex items-center space-x-2 flex-1">
                <Input
                value={editedTitle}
                onChange={(e) => setEditedTitle(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') handleTitleSave();
                  if (e.key === 'Escape') handleTitleCancel();
                }}
                className="h-8"
                autoFocus
                onClick={(e) => e.stopPropagation()} />

                <Button size="sm" variant="ghost" onClick={handleTitleSave}>
                  <Check className="w-4 h-4" />
                </Button>
                <Button size="sm" variant="ghost" onClick={handleTitleCancel}>
                  <X className="w-4 h-4" />
                </Button>
              </div> :

            <div className="flex items-center space-x-2 flex-1">
                <h3 className="text-lg font-semibold">{section.title}</h3>
                <Button
                size="sm"
                variant="ghost"
                onClick={(e) => {
                  e.stopPropagation();
                  setIsEditingTitle(true);
                }}>

                  <Edit2 className="w-4 h-4" />
                </Button>
              </div>
            }
          </div>
          {/* Section Actions */}
          <div className="flex items-center space-x-2">
            {/* Layout Selector */}
            <Select
              value={section.layout || 'single'}
              onValueChange={(value) => onUpdate({ layout: value })}>

              <SelectTrigger className="w-32 h-8" onClick={(e) => e.stopPropagation()}>
                <div className="flex items-center space-x-2">
                  {getLayoutIcon()}
                  <SelectValue />
                </div>
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="single">
                  <div className="flex items-center space-x-2">
                    <Square className="w-4 h-4" />
                    <span>{t("components.single")}</span>
                  </div>
                </SelectItem>
                <SelectItem value="two-column">
                  <div className="flex items-center space-x-2">
                    <Columns className="w-4 h-4" />
                    <span>{t("components.two_column")}</span>
                  </div>
                </SelectItem>
                <SelectItem value="grid">
                  <div className="flex items-center space-x-2">
                    <Grid3x3 className="w-4 h-4" />
                    <span>Grid</span>
                  </div>
                </SelectItem>
              </SelectContent>
            </Select>
            {/* Collapse/Expand Button */}
            <Button
              size="sm"
              variant="ghost"
              onClick={(e) => {
                e.stopPropagation();
                setIsCollapsed(!isCollapsed);
              }}>

              {isCollapsed ?
              <ChevronDown className="w-4 h-4" /> :

              <ChevronUp className="w-4 h-4" />
              }
            </Button>
            {/* More Options */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
                <Button size="sm" variant="ghost">
                  <Settings className="w-4 h-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={onDuplicate}>
                  <Copy className="w-4 h-4 mr-2" />{t("components.duplicate_section")}

                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem
                  onClick={onDelete}
                  className="text-red-600 dark:text-red-400">

                  <Trash2 className="w-4 h-4 mr-2" />{t("components.delete_section")}

                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </CardHeader>
      {!isCollapsed &&
      <CardContent>
          <Droppable droppableId={`section-${section.id}`} type="WIDGET">
            {(provided, snapshot) =>
          <div
            ref={provided.innerRef}
            {...provided.droppableProps}
            className={`
                  min-h-[100px] rounded-lg transition-colors
                  ${snapshot.isDraggingOver ?
            'bg-blue-50 dark:bg-blue-900/20 border-2 border-dashed border-blue-300 dark:border-blue-700' :
            ''}
                  ${
            section.widgets.length === 0 ? 'border-2 border-dashed border-gray-300 dark:border-gray-600' : ''}
                `}>

                {section.widgets.length === 0 ?
            <div className="flex flex-col items-center justify-center py-8 text-gray-500 dark:text-gray-400">
                    <Plus className="w-8 h-8 mb-2" />
                    <p className="text-sm font-medium">Drop widgets here</p>
                    <p className="text-xs">or click the widget library to add</p>
                  </div> :

            <div className={getLayoutClass()}>
                    {section.widgets.map((widget, index) =>
              <Draggable
                key={widget.id}
                draggableId={widget.id}
                index={index}>

                        {(provided, snapshot) =>
                <div
                  ref={provided.innerRef}
                  {...provided.draggableProps}
                  className={`
                              ${snapshot.isDragging ? 'opacity-50' : ''}
                              ${section.layout !== 'single' ? '' : 'mb-4 last:mb-0'}
                            `}>

                            <ReportWidget
                    widget={widget}
                    darkMode={darkMode}
                    onUpdate={(updates) => onUpdateWidget(widget.id, updates)}
                    onDelete={() => onDeleteWidget(widget.id)}
                    dragHandleProps={provided.dragHandleProps}
                    isDragging={snapshot.isDragging} />

                          </div>
                }
                      </Draggable>
              )}
                  </div>
            }
                {provided.placeholder}
              </div>
          }
          </Droppable>
          {/* Add Widget Button */}
          {section.widgets.length > 0 &&
        <div className="mt-4 flex justify-center">
              <Button
            variant="outline"
            size="sm"
            onClick={(e) => {
              e.stopPropagation();
              // This would open widget selector or trigger add widget action
            }}>

                <Plus className="w-4 h-4 mr-2" />
                Add Widget
              </Button>
            </div>
        }
        </CardContent>
      }
    </Card>);

};
export default ReportSection;