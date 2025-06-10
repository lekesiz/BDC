// TODO: i18n - processed
import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Eye,
  Edit,
  ChevronRight,
  Phone,
  Mail,
  Calendar,
  User } from
'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableCell,
  TablePagination } from
'@/components/ui/table';
import { useBreakpoint } from '@/hooks/useMediaQuery';
import { cn } from '@/lib/utils';
/**
 * Mobile-responsive beneficiaries table component
 * Shows as cards on mobile, table on desktop
 */import { useTranslation } from "react-i18next";
export const ResponsiveBeneficiariesTable = ({
  beneficiaries = [],
  isLoading,
  page,
  totalPages,
  pageSize,
  onPageChange,
  onSort,
  sortField,
  sortDirection,
  onEdit,
  onView
}) => {const { t } = useTranslation();
  const navigate = useNavigate();
  const { isMobile, isTablet } = useBreakpoint();
  // Render status badge
  const renderStatusBadge = (status) => {
    const statusStyles = {
      active: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
      inactive: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300',
      pending: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
      completed: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
    };
    return (
      <span className={cn(
        'inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium',
        statusStyles[status] || statusStyles.inactive
      )}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>);

  };
  // Format date for display
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };
  // Mobile card view
  if (isMobile || isTablet) {
    return (
      <div className="space-y-4">
        {isLoading ?
        <div className="space-y-4">
            {[1, 2, 3].map((i) =>
          <Card key={i} className="p-4 animate-pulse">
                <div className="space-y-3">
                  <div className="h-5 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
                  <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
                  <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-2/3"></div>
                </div>
              </Card>
          )}
          </div> :
        beneficiaries.length === 0 ?
        <Card className="p-8 text-center">
            <User className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500 dark:text-gray-400">{t("components.no_beneficiaries_found")}</p>
          </Card> :

        <>
            {beneficiaries.map((beneficiary) =>
          <Card
            key={beneficiary.id}
            className="p-4 hover:shadow-md transition-shadow cursor-pointer"
            onClick={() => onView ? onView(beneficiary.id) : navigate(`/beneficiaries/${beneficiary.id}`)}>

                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0 space-y-2">
                    {/* Name and status */}
                    <div className="flex items-start justify-between">
                      <div>
                        <h3 className="text-base font-semibold text-gray-900 dark:text-gray-100">
                          {beneficiary.first_name} {beneficiary.last_name}
                        </h3>
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          ID: {beneficiary.beneficiary_id || beneficiary.id}
                        </p>
                      </div>
                      {renderStatusBadge(beneficiary.status)}
                    </div>
                    {/* Contact info */}
                    <div className="space-y-1">
                      {beneficiary.email &&
                  <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
                          <Mail className="h-4 w-4 mr-2 flex-shrink-0" />
                          <span className="truncate">{beneficiary.email}</span>
                        </div>
                  }
                      {beneficiary.phone &&
                  <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
                          <Phone className="h-4 w-4 mr-2 flex-shrink-0" />
                          <span>{beneficiary.phone}</span>
                        </div>
                  }
                      <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
                        <Calendar className="h-4 w-4 mr-2 flex-shrink-0" />
                        <span>Joined: {formatDate(beneficiary.created_at)}</span>
                      </div>
                    </div>
                    {/* Program info */}
                    {beneficiary.program &&
                <div className="pt-2 border-t border-gray-200 dark:border-gray-700">
                        <p className="text-sm">
                          <span className="font-medium text-gray-700 dark:text-gray-300">Program:</span>{' '}
                          <span className="text-gray-600 dark:text-gray-400">{beneficiary.program}</span>
                        </p>
                      </div>
                }
                  </div>
                  {/* Arrow icon */}
                  <ChevronRight className="h-5 w-5 text-gray-400 ml-2 flex-shrink-0" />
                </div>
              </Card>
          )}
            {/* Pagination */}
            <div className="mt-4">
              <TablePagination
              totalItems={totalPages * pageSize}
              itemsPerPage={pageSize}
              currentPage={page}
              onPageChange={onPageChange}
              totalPages={totalPages} />

            </div>
          </>
        }
      </div>);

  }
  // Desktop table view
  return (
    <div>
      <Table>
        <TableHeader>
          <TableRow>
            <TableCell
              isHeader
              className="cursor-pointer"
              onClick={() => onSort('last_name')}>

              <div className="flex items-center">{t("components.name")}

                {sortField === 'last_name' &&
                <span className="ml-1">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                }
              </div>
            </TableCell>
            <TableCell isHeader>{t("components.email")}</TableCell>
            <TableCell isHeader>{t("components.phone")}</TableCell>
            <TableCell isHeader>{t("components.program")}</TableCell>
            <TableCell
              isHeader
              className="cursor-pointer"
              onClick={() => onSort('status')}>

              <div className="flex items-center">{t("components.status")}

                {sortField === 'status' &&
                <span className="ml-1">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                }
              </div>
            </TableCell>
            <TableCell
              isHeader
              className="cursor-pointer"
              onClick={() => onSort('created_at')}>

              <div className="flex items-center">{t("components.joined")}

                {sortField === 'created_at' &&
                <span className="ml-1">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                }
              </div>
            </TableCell>
            <TableCell isHeader>{t("components.actions")}</TableCell>
          </TableRow>
        </TableHeader>
        <TableBody>
          {isLoading ?
          <TableRow>
              <TableCell colSpan={7} className="text-center py-8">
                <div className="inline-flex items-center">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                  <span className="ml-2">{t("components.loading_beneficiaries")}</span>
                </div>
              </TableCell>
            </TableRow> :
          beneficiaries.length === 0 ?
          <TableRow>
              <TableCell colSpan={7} className="text-center py-8">
                <User className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">{t("components.no_beneficiaries_found")}</p>
              </TableCell>
            </TableRow> :

          beneficiaries.map((beneficiary) =>
          <TableRow key={beneficiary.id}>
                <TableCell>
                  <div>
                    <p className="font-medium text-gray-900 dark:text-gray-100">
                      {beneficiary.first_name} {beneficiary.last_name}
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      ID: {beneficiary.beneficiary_id || beneficiary.id}
                    </p>
                  </div>
                </TableCell>
                <TableCell>{beneficiary.email || 'N/A'}</TableCell>
                <TableCell>{beneficiary.phone || 'N/A'}</TableCell>
                <TableCell>{beneficiary.program || 'Not assigned'}</TableCell>
                <TableCell>{renderStatusBadge(beneficiary.status)}</TableCell>
                <TableCell>{formatDate(beneficiary.created_at)}</TableCell>
                <TableCell>
                  <div className="flex items-center space-x-2">
                    <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => onView ? onView(beneficiary.id) : navigate(`/beneficiaries/${beneficiary.id}`)}
                  aria-label={`View ${beneficiary.first_name} ${beneficiary.last_name}`}>

                      <Eye className="h-4 w-4" />
                    </Button>
                    {onEdit &&
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => onEdit(beneficiary.id)}
                  aria-label={`Edit ${beneficiary.first_name} ${beneficiary.last_name}`}>

                        <Edit className="h-4 w-4" />
                      </Button>
                }
                  </div>
                </TableCell>
              </TableRow>
          )
          }
        </TableBody>
      </Table>
      {/* Pagination */}
      {beneficiaries.length > 0 &&
      <div className="mt-4">
          <TablePagination
          totalItems={totalPages * pageSize}
          itemsPerPage={pageSize}
          currentPage={page}
          onPageChange={onPageChange}
          totalPages={totalPages} />

        </div>
      }
    </div>);

};