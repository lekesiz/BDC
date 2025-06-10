/**
 * FieldPalette Component
 * 
 * Displays available fields that can be dragged into the report builder
 */

import React, { useState, useMemo } from 'react';
import { useDrag } from 'react-dnd';
import { Card, CardContent, CardHeader, CardTitle } from '../../../../components/ui/card';
import { Input } from '../../../../components/ui/input';
import { Badge } from '../../../../components/ui/badge';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '../../../../components/ui/accordion';
import { Search, Database, Hash, Calendar, Type, Mail, Phone, MapPin, User, Settings } from 'lucide-react';

const FIELD_ICONS = {
  identity: User,
  contact: Mail,
  demographics: User,
  status: Settings,
  timeline: Calendar,
  details: Type,
  schedule: Calendar,
  performance: Hash,
  metrics: Hash
};

const FIELD_TYPE_ICONS = {
  text: Type,
  number: Hash,
  date: Calendar,
  datetime: Calendar,
  email: Mail,
  phone: Phone,
  boolean: Settings,
  select: Settings,
  percentage: Hash,
  currency: Hash
};

const DraggableField = ({ field, source }) => {
  const [{ isDragging }, drag] = useDrag({
    type: 'field',
    item: { ...field, source },
    collect: (monitor) => ({
      isDragging: monitor.isDragging()
    })
  });

  const IconComponent = FIELD_TYPE_ICONS[field.type] || Type;
  const categoryIcon = FIELD_ICONS[field.category] || Database;
  const CategoryIcon = categoryIcon;

  return (
    <div
      ref={drag}
      className={`
        flex items-center p-3 bg-white border rounded-lg cursor-move transition-all hover:shadow-md
        ${isDragging ? 'opacity-50 shadow-lg' : ''}
      `}
    >
      <div className="flex items-center space-x-3 flex-1">
        <div className="flex-shrink-0">
          <IconComponent className="h-4 w-4 text-gray-500" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-gray-900 truncate">
            {field.name}
          </p>
          <div className="flex items-center space-x-2 mt-1">
            <Badge variant="outline" className="text-xs">
              {field.type}
            </Badge>
            {field.category && (
              <div className="flex items-center space-x-1">
                <CategoryIcon className="h-3 w-3 text-gray-400" />
                <span className="text-xs text-gray-500 capitalize">
                  {field.category}
                </span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

const FieldPalette = ({ availableFields, onFieldDrag, readonly = false }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [expandedSources, setExpandedSources] = useState(['beneficiaries']);

  // Filter and group fields
  const filteredAndGroupedFields = useMemo(() => {
    if (!availableFields) return {};

    const filtered = {};
    
    Object.entries(availableFields).forEach(([source, fields]) => {
      const filteredFields = fields.filter(field => {
        if (!searchTerm) return true;
        
        const searchLower = searchTerm.toLowerCase();
        return (
          field.name.toLowerCase().includes(searchLower) ||
          field.id.toLowerCase().includes(searchLower) ||
          field.type.toLowerCase().includes(searchLower) ||
          (field.category && field.category.toLowerCase().includes(searchLower))
        );
      });

      if (filteredFields.length > 0) {
        filtered[source] = filteredFields;
      }
    });

    return filtered;
  }, [availableFields, searchTerm]);

  // Group fields by category within each source
  const groupedByCategory = useMemo(() => {
    const grouped = {};
    
    Object.entries(filteredAndGroupedFields).forEach(([source, fields]) => {
      grouped[source] = {};
      
      fields.forEach(field => {
        const category = field.category || 'other';
        if (!grouped[source][category]) {
          grouped[source][category] = [];
        }
        grouped[source][category].push(field);
      });
    });

    return grouped;
  }, [filteredAndGroupedFields]);

  const totalFields = useMemo(() => {
    return Object.values(filteredAndGroupedFields).reduce(
      (total, fields) => total + fields.length,
      0
    );
  }, [filteredAndGroupedFields]);

  if (readonly) {
    return (
      <div className="p-4">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Available Fields</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-500">
              This report is in read-only mode. Fields cannot be modified.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="p-4 border-b">
        <h3 className="text-lg font-semibold text-gray-900 mb-3">
          Available Fields
        </h3>
        
        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            placeholder="Search fields..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>

        {/* Stats */}
        <div className="mt-3 flex items-center justify-between text-sm text-gray-500">
          <span>{totalFields} fields available</span>
          {searchTerm && (
            <span>
              in {Object.keys(filteredAndGroupedFields).length} source{Object.keys(filteredAndGroupedFields).length !== 1 ? 's' : ''}
            </span>
          )}
        </div>
      </div>

      {/* Field List */}
      <div className="flex-1 overflow-auto">
        {Object.keys(filteredAndGroupedFields).length === 0 ? (
          <div className="p-4 text-center text-gray-500">
            {searchTerm ? 'No fields match your search.' : 'No fields available.'}
          </div>
        ) : (
          <Accordion
            type="multiple"
            value={expandedSources}
            onValueChange={setExpandedSources}
            className="w-full"
          >
            {Object.entries(groupedByCategory).map(([source, categories]) => (
              <AccordionItem key={source} value={source} className="border-0">
                <AccordionTrigger className="px-4 py-3 hover:bg-gray-50">
                  <div className="flex items-center space-x-2">
                    <Database className="h-4 w-4 text-blue-600" />
                    <span className="font-medium capitalize">
                      {source.replace('_', ' ')}
                    </span>
                    <Badge variant="secondary" className="ml-auto">
                      {Object.values(categories).reduce((sum, fields) => sum + fields.length, 0)}
                    </Badge>
                  </div>
                </AccordionTrigger>
                <AccordionContent className="px-4 pb-2">
                  <div className="space-y-3">
                    {Object.entries(categories).map(([category, fields]) => (
                      <div key={category}>
                        {Object.keys(categories).length > 1 && (
                          <div className="mb-2">
                            <div className="flex items-center space-x-2 text-xs font-medium text-gray-700 uppercase tracking-wide">
                              {FIELD_ICONS[category] && (
                                <FIELD_ICONS[category] className="h-3 w-3" />
                              )}
                              <span>{category.replace('_', ' ')}</span>
                            </div>
                          </div>
                        )}
                        <div className="space-y-2">
                          {fields.map((field) => (
                            <DraggableField
                              key={`${source}_${field.id}`}
                              field={field}
                              source={source}
                            />
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t bg-gray-50">
        <div className="text-xs text-gray-500 space-y-1">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
            <span>Drag fields to the report canvas</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            <span>Drop fields to add or reorder</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FieldPalette;