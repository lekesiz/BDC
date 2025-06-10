// TODO: i18n - processed
import { useState, useEffect } from 'react';
import {
  Grip,
  X,
  Settings,
  PlusSquare,
  Save,
  RotateCcw,
  LayoutGrid,
  Columns,
  Grid2X2,
  Grid3X3 } from
'lucide-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  UpcomingSessionsWidget,
  ProgramProgressWidget,
  SkillsProgressWidget,
  RecentNotificationsWidget,
  ProfileSummaryWidget,
  ResourcesWidget,
  AchievementsWidget,
  AssessmentsWidget } from
'./widgets';
/**
 * Configurable dashboard grid component for displaying widgets
 */import { useTranslation } from "react-i18next";
const DashboardWidgetGrid = ({
  dashboardData,
  isLoading,
  error,
  onSaveLayout,
  savedLayout
}) => {const { t } = useTranslation();
  const [isEditing, setIsEditing] = useState(false);
  const [columns, setColumns] = useState(2);
  const [activeWidgets, setActiveWidgets] = useState([
  { id: 'profile', name: 'Profile Summary', component: ProfileSummaryWidget, span: 1 },
  { id: 'program', name: 'Program Progress', component: ProgramProgressWidget, span: 2 },
  { id: 'sessions', name: 'Upcoming Sessions', component: UpcomingSessionsWidget, span: 1 },
  { id: 'skills', name: 'Skills Progress', component: SkillsProgressWidget, span: 1 },
  { id: 'notifications', name: 'Recent Notifications', component: RecentNotificationsWidget, span: 1 },
  { id: 'assessments', name: 'Assessments', component: AssessmentsWidget, span: 1 },
  { id: 'resources', name: 'Learning Resources', component: ResourcesWidget, span: 1 },
  { id: 'achievements', name: 'My Achievements', component: AchievementsWidget, span: 1 }]
  );
  const [availableWidgets, setAvailableWidgets] = useState([]);
  // Load saved layout if available
  useEffect(() => {
    if (savedLayout) {
      try {
        const layoutData = JSON.parse(savedLayout);
        if (layoutData.columns) {
          setColumns(layoutData.columns);
        }
        if (layoutData.widgets && Array.isArray(layoutData.widgets)) {
          // Filter the saved widgets to ensure they exist in our available widgets
          const validWidgets = layoutData.widgets.filter((widget) =>
          activeWidgets.some((aw) => aw.id === widget.id)
          );
          // Merge saved widget details with the full component data
          const mergedWidgets = validWidgets.map((widget) => {
            const fullWidget = activeWidgets.find((aw) => aw.id === widget.id);
            return { ...fullWidget, ...widget };
          });
          setActiveWidgets(mergedWidgets);
          // Update available widgets
          const activeIds = mergedWidgets.map((w) => w.id);
          const available = activeWidgets.filter((w) => !activeIds.includes(w.id));
          setAvailableWidgets(available);
        }
      } catch (error) {
        console.error('Error loading saved layout:', error);
      }
    } else {
      // If no saved layout, initialize available widgets as empty
      setAvailableWidgets([]);
    }
  }, [savedLayout]);
  // Handle save layout
  const handleSaveLayout = () => {
    // Create a layout object with only the necessary data
    const layoutData = {
      columns,
      widgets: activeWidgets.map((widget) => ({
        id: widget.id,
        span: widget.span,
        order: widget.order
      }))
    };
    onSaveLayout(JSON.stringify(layoutData));
    setIsEditing(false);
  };
  // Handle reset to default layout
  const handleResetLayout = () => {
    setColumns(2);
    setActiveWidgets([
    { id: 'profile', name: 'Profile Summary', component: ProfileSummaryWidget, span: 1, order: 0 },
    { id: 'program', name: 'Program Progress', component: ProgramProgressWidget, span: 2, order: 1 },
    { id: 'sessions', name: 'Upcoming Sessions', component: UpcomingSessionsWidget, span: 1, order: 2 },
    { id: 'skills', name: 'Skills Progress', component: SkillsProgressWidget, span: 1, order: 3 },
    { id: 'notifications', name: 'Recent Notifications', component: RecentNotificationsWidget, span: 1, order: 4 },
    { id: 'assessments', name: 'Assessments', component: AssessmentsWidget, span: 1, order: 5 },
    { id: 'resources', name: 'Learning Resources', component: ResourcesWidget, span: 1, order: 6 },
    { id: 'achievements', name: 'My Achievements', component: AchievementsWidget, span: 1, order: 7 }]
    );
    setAvailableWidgets([]);
  };
  // Handle remove widget
  const handleRemoveWidget = (widgetId) => {
    const widgetToRemove = activeWidgets.find((w) => w.id === widgetId);
    if (widgetToRemove) {
      setActiveWidgets(activeWidgets.filter((w) => w.id !== widgetId));
      setAvailableWidgets([...availableWidgets, widgetToRemove]);
    }
  };
  // Handle add widget
  const handleAddWidget = (widgetId) => {
    const widgetToAdd = availableWidgets.find((w) => w.id === widgetId);
    if (widgetToAdd) {
      setActiveWidgets([...activeWidgets, {
        ...widgetToAdd,
        order: activeWidgets.length // Set the order to the end of the list
      }]);
      setAvailableWidgets(availableWidgets.filter((w) => w.id !== widgetId));
    }
  };
  // Handle change widget span
  const handleChangeWidgetSpan = (widgetId, newSpan) => {
    setActiveWidgets(
      activeWidgets.map((widget) =>
      widget.id === widgetId ?
      { ...widget, span: newSpan } :
      widget
      )
    );
  };
  // Handle move widget up
  const handleMoveWidgetUp = (widgetId) => {
    const index = activeWidgets.findIndex((w) => w.id === widgetId);
    if (index > 0) {
      const newActiveWidgets = [...activeWidgets];
      [newActiveWidgets[index], newActiveWidgets[index - 1]] = [newActiveWidgets[index - 1], newActiveWidgets[index]];
      // Update orders
      newActiveWidgets.forEach((widget, idx) => {
        widget.order = idx;
      });
      setActiveWidgets(newActiveWidgets);
    }
  };
  // Handle move widget down
  const handleMoveWidgetDown = (widgetId) => {
    const index = activeWidgets.findIndex((w) => w.id === widgetId);
    if (index < activeWidgets.length - 1) {
      const newActiveWidgets = [...activeWidgets];
      [newActiveWidgets[index], newActiveWidgets[index + 1]] = [newActiveWidgets[index + 1], newActiveWidgets[index]];
      // Update orders
      newActiveWidgets.forEach((widget, idx) => {
        widget.order = idx;
      });
      setActiveWidgets(newActiveWidgets);
    }
  };
  // Get sorted active widgets
  const getSortedActiveWidgets = () => {
    return [...activeWidgets].sort((a, b) => (a.order || 0) - (b.order || 0));
  };
  const sortedWidgets = getSortedActiveWidgets();
  return (
    <div>
      {/* Controls */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold">{t("components.dashboard")}</h1>
          <p className="text-gray-600">{t("components.welcome_to_your_learning_dashboard")}</p>
        </div>
        {isEditing ?
        <div className="flex space-x-2">
            <div className="flex mr-4 border rounded-lg overflow-hidden">
              <Button
              variant={columns === 1 ? 'default' : 'ghost'}
              size="sm"
              className="rounded-none"
              onClick={() => setColumns(1)}>

                <Columns className="h-4 w-4" />
              </Button>
              <Button
              variant={columns === 2 ? 'default' : 'ghost'}
              size="sm"
              className="rounded-none"
              onClick={() => setColumns(2)}>

                <Grid2X2 className="h-4 w-4" />
              </Button>
              <Button
              variant={columns === 3 ? 'default' : 'ghost'}
              size="sm"
              className="rounded-none"
              onClick={() => setColumns(3)}>

                <Grid3X3 className="h-4 w-4" />
              </Button>
            </div>
            <Button
            variant="outline"
            onClick={handleResetLayout}>

              <RotateCcw className="h-4 w-4 mr-2" />{t("components.reset")}

          </Button>
            <Button
            variant="outline"
            onClick={() => setIsEditing(false)}>

              <X className="h-4 w-4 mr-2" />{t("components.cancel")}

          </Button>
            <Button
            onClick={handleSaveLayout}>

              <Save className="h-4 w-4 mr-2" />{t("components.save_layout")}

          </Button>
          </div> :

        <Button
          variant="outline"
          onClick={() => setIsEditing(true)}>

            <Settings className="h-4 w-4 mr-2" />{t("components.customize_dashboard")}

        </Button>
        }
      </div>
      {/* Available widgets (when editing) */}
      {isEditing && availableWidgets.length > 0 &&
      <div className="mb-8">
          <h2 className="text-lg font-medium mb-3">Available Widgets</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {availableWidgets.map((widget) =>
          <Card key={widget.id} className="p-4 text-center">
                <h3 className="font-medium mb-2">{widget.name}</h3>
                <Button
              size="sm"
              onClick={() => handleAddWidget(widget.id)}>

                  <PlusSquare className="h-4 w-4 mr-2" />{t("components.add_to_dashboard")}

            </Button>
              </Card>
          )}
          </div>
        </div>
      }
      {/* Widget grid */}
      <div className={`grid grid-cols-1 ${
      columns === 1 ? '' : columns === 2 ? 'md:grid-cols-2' : 'md:grid-cols-3'} gap-6`
      }>
        {sortedWidgets.map((widget) => {
          const WidgetComponent = widget.component;
          return (
            <div
              key={widget.id}
              className={`${
              // Apply column spanning
              columns > 1 && widget.span > 1 ?
              widget.span === 2 ?
              'md:col-span-2' :
              columns === 3 ? 'md:col-span-3' : 'md:col-span-2' :
              ''}`
              }>

              {isEditing ?
              <div className="relative mb-2">
                  <Card className="p-3 border-2 border-dashed border-primary/40">
                    <div className="flex justify-between items-center">
                      <div className="flex items-center">
                        <Grip className="h-4 w-4 mr-2 text-gray-400" />
                        <h3 className="font-medium">{widget.name}</h3>
                      </div>
                      <div className="flex items-center">
                        {columns > 1 &&
                      <div className="flex border rounded-md overflow-hidden mr-2">
                            <button
                          className={`px-2 py-1 text-xs ${widget.span === 1 ? 'bg-gray-200' : 'bg-white'}`}
                          onClick={() => handleChangeWidgetSpan(widget.id, 1)}
                          disabled={widget.span === 1}>

                              1
                            </button>
                            <button
                          className={`px-2 py-1 text-xs ${widget.span === 2 ? 'bg-gray-200' : 'bg-white'}`}
                          onClick={() => handleChangeWidgetSpan(widget.id, 2)}
                          disabled={widget.span === 2}>

                              2
                            </button>
                            {columns === 3 &&
                        <button
                          className={`px-2 py-1 text-xs ${widget.span === 3 ? 'bg-gray-200' : 'bg-white'}`}
                          onClick={() => handleChangeWidgetSpan(widget.id, 3)}
                          disabled={widget.span === 3}>

                                3
                              </button>
                        }
                          </div>
                      }
                        <div className="flex mr-2">
                          <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleMoveWidgetUp(widget.id)}
                          disabled={sortedWidgets.indexOf(widget) === 0}
                          className="h-8 w-8 p-0">

                            <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                              <path d="m18 15-6-6-6 6" />
                            </svg>
                          </Button>
                          <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleMoveWidgetDown(widget.id)}
                          disabled={sortedWidgets.indexOf(widget) === sortedWidgets.length - 1}
                          className="h-8 w-8 p-0">

                            <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                              <path d="m6 9 6 6 6-6" />
                            </svg>
                          </Button>
                        </div>
                        <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleRemoveWidget(widget.id)}
                        className="h-8 w-8 p-0 text-red-500 hover:text-red-700">

                          <X className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </Card>
                </div> :
              null}
              <WidgetComponent
                data={
                widget.id === 'profile' ? dashboardData?.profile :
                widget.id === 'program' ? dashboardData?.dashboard :
                widget.id === 'sessions' ? dashboardData?.dashboard?.upcomingSessions :
                widget.id === 'skills' ? dashboardData?.skills :
                widget.id === 'notifications' ? dashboardData?.notifications :
                widget.id === 'resources' ? dashboardData?.resources :
                widget.id === 'achievements' ? dashboardData?.achievements :
                widget.id === 'assessments' ? dashboardData?.assessments :
                null
                }
                isLoading={isLoading}
                error={error} />

            </div>);

        })}
      </div>
    </div>);

};
export default DashboardWidgetGrid;