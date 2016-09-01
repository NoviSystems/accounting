import json
import datetime

from django.shortcuts import redirect
from django.db.models import Max
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView, FormView, CreateView, UpdateView, DeleteView, View

from models import *
from forms import *
from decimal import *


class PermissionsMixin(LoginRequiredMixin, object):

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            try:
                self.permission_levels = AccountingUser.objects.filter(user=self.request.user)
                self.business_units = []
                for perm in self.permission_levels:
                    self.business_units.append(perm.business_unit)
            except ObjectDoesNotExist:
                self.permission_levels = None
                self.business_units = None
        else:
            self.permission_levels = None
        return super(PermissionsMixin, self).dispatch(request, *args, **kwargs)


class SetUpMixin(object):

    def dispatch(self, request, *args, **kwargs):
        self.current = BusinessUnit.objects.get(pk=kwargs['business_unit'])
        self.fiscal_years = FiscalYear.objects.filter(business_unit=self.current)
        now = datetime.datetime.now()
        for fiscal_year in self.fiscal_years:
            self.months = Month.objects.filter(fiscal_year=fiscal_year)
            for month in self.months:
                if month.month.month == now.month:
                    self.current_month = month

        self.now = now

        # if fiscal year is passed by url, get that year as the current fiscal year
        # else get the value associated to the current month
        if 'fiscal_year' in kwargs:
            self.current_fiscal_year = FiscalYear.objects.get(pk=kwargs['fiscal_year'])
        elif self.fiscal_years:
            self.current_fiscal_year = self.current_month.fiscal_year
        else:
            self.current_fiscal_year = None

        # Notification System Population
        self.notifications = []
        # Get all line items associated with a business unit
        lineItems = LineItem.objects.filter(business_unit=self.current)
        # Loop through each line item
        # for lineItem in lineItems:
        #     # If the line item's date payable is in the past to the current date
        #     # And the date payed has not been entered
        #     # And it has not been reconciled
        #     # Add to the list of notifications
        #     # if lineItem.date_payable

        return super(SetUpMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(SetUpMixin, self).get_context_data(*args, **kwargs)

        context['current'] = self.current
        context['current_month'] = self.current_month
        context['current_fiscal_year'] = self.current_fiscal_year

        context['fiscal_years'] = self.fiscal_years

        try:
            context['is_viewer'] = self.is_viewer
        except AttributeError:
            context['is_viewer'] = False
        return context


class ViewerMixin(SetUpMixin, PermissionsMixin, UserPassesTestMixin):

    def test_func(self):
        try:
            bu_permission = AccountingUser.objects.get(user=self.request.user, business_unit=self.current).permission
            if self.request.user.is_superuser:
                return True
            elif bu_permission == 'MANAGER':
                return True
            elif bu_permission == 'VIEWER':
                self.is_viewer = True
                return True
            else:
                raise Http404()
        except ObjectDoesNotExist:
            raise Http404()


class ManagerMixin(SetUpMixin, PermissionsMixin, UserPassesTestMixin):

    def test_func(self):
        try:
            bu_permission = AccountingUser.objects.get(user=self.request.user, business_unit=self.current).permission
            if self.request.user.is_superuser:
                return True
            elif bu_permission == 'MANAGER':
                return True
            else:
                raise Http404()
        except ObjectDoesNotExist:
            raise Http404()


class HomePageView(PermissionsMixin, TemplateView):
    template_name = 'accounting/home.html'

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data()
        context['business_units'] = self.business_units
        return context


class DashboardView(ViewerMixin, SetUpMixin, TemplateView):
    template_name = 'accounting/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data()

        context['notifications'] = self.notifications

        if self.fiscal_years:
            # Finding the current month
            current_month = None
            now = self.now

            cma = {
                'title': 'Cash Month Actual',
                'values': []
            }
            cmpr = {
                'title': 'Cash Month Projected',
                'values': []
            }
            ema = {
                'title': 'Expenses Month Actual',
                'values': []
            }
            emp = {
                'title': 'Expenses Month Projected',
                'values': []
            }
            ima = {
                'title': 'Recievables Month Actual',
                'values': []
            }
            imp = {
                'title': 'Recievables Month Projected',
                'values': []
            }
            pma = {
                'title': 'Payroll Month Actual',
                'values': []
            }
            pmp = {
                'title': 'Payroll Month Projected',
                'values': []
            }
            tama = {
                'title': 'Total Assets Projected',
                'values': []
            }
            tamp = {
                'title': 'Total Assets Actual',
                'values': []
            }

            # Month names used on graph and table
            months_names = []

            # Computes totals for the whole fiscal year
            months = []

            # moves through all fiscal years
            for fiscal_year in self.fiscal_years:

                # gets all months
                months = Month.objects.filter(fiscal_year=fiscal_year)

                # moves through all months
                for month in months:

                    # gets current month
                    if month.month.month == now.month:
                        current_month = month

            # if fiscal year is passed by url, get that year as the current fiscal year
            # else get the value associated to the current month
            if 'fiscal_year' in kwargs:
                current_fiscal_year = FiscalYear.objects.get(pk=kwargs['fiscal_year'])
            else:
                current_fiscal_year = current_month.fiscal_year

            # gets all months
            months = Month.objects.filter(fiscal_year=current_fiscal_year)

            # moves through all months
            for month in months:

                # gets current month
                if month.month.month == now.month:
                    current_month = month

            current_fiscal_year = current_month.fiscal_year

            # moves through all fiscal years

            # gets all months
            months = list(Month.objects.filter(fiscal_year=current_fiscal_year))

            # moves through all months
            for month in months:

                # gets all month names
                months_names.append(month.month.strftime("%B"))

                # payroll variables
                payroll_month_actual = Decimal('0.00')
                payroll_month_projected = Decimal('0.00')

                # add up payroll expenses for the month
                for payroll in Payroll.objects.filter(month=month):
                    if payroll.expense.reconciled:
                        payroll_month_actual += payroll.expense.actual_amount
                    payroll_month_projected += payroll.expense.predicted_amount

                # adds payroll values to month lists for table
                pma['values'].append(payroll_month_actual)
                pmp['values'].append(payroll_month_projected)

                # expenses variables
                expenses_month_actual = Decimal('0.00')
                expense_month_projected = Decimal('0.00')

                # add up all expense values
                for expense in Expense.objects.filter(month=month):
                    if expense.reconciled:
                        expenses_month_actual += expense.actual_amount
                    expense_month_projected += expense.predicted_amount

                # subtract payroll values to get plain expense
                expenses_month_actual -= payroll_month_actual
                expense_month_projected -= payroll_month_projected

                # all the expenses to lists for table
                ema['values'].append(expenses_month_actual)
                emp['values'].append(expense_month_projected)

                # income variables
                income_month_actual = Decimal('0.00')
                income_month_projected = Decimal('0.00')

                # add up all income values
                for income in Income.objects.filter(month=month):
                    if income.reconciled:
                        income_month_actual += income.actual_amount
                    income_month_projected += income.predicted_amount

                # add income to lists for table
                ima['values'].append(income_month_actual)
                imp['values'].append(income_month_projected)

                # cash variables
                cash_month_actual = Decimal('0.00')
                cash_month_projected = Decimal('0.00')

                # compute cash values
                for cash in Cash.objects.filter(month=month):
                    if cash.reconciled:
                        cash_month_actual += cash.actual_amount
                    cash_month_projected += cash.predicted_amount

                # add cash to lists for table
                cmpr['values'].append(cash_month_projected)
                cma['values'].append(cash_month_actual)

                # income booked variables
                income_booked_projected = Decimal('0.00')

                # compute income booked projected
                for value in imp['values']:
                    income_booked_projected += value
                total_assets_month_projected = cash_month_projected + income_booked_projected
                tamp['values'].append(total_assets_month_projected)

                # computer income booked actual
                income_booked_actual = Decimal('0.00')
                for value in ima['values']:
                    income_booked_actual += value
                total_assets_month_actual = cash_month_actual + income_booked_actual
                tama['values'].append(total_assets_month_actual)

            # list of dashboard data
            dashboard_data = [cma, cmpr, ema, emp, ima, imp, pma, pmp, tama, tamp]

            # context values for month view
            context['cma'] = cma    # cash month actual
            context['cmpr'] = cmpr  # cash month predicted
            context['ima'] = ima    # income month actual
            context['imp'] = imp    # income month predicted
            context['ema'] = ema    # expenses month actual
            context['emp'] = emp    # expenses month predicted
            context['pma'] = pma    # payroll month actual
            context['pmp'] = pmp    # payroll month predicted
            context['tama'] = tama  # total assest month actual
            context['tamp'] = tamp  # total assets month predicted

            # Context totals for the Graph values
            context['business_units'] = self.business_units
            context['months_names'] = months_names
            context['months'] = months
            context['months_j'] = json.dumps(months_names)
            context['predicted_totals'] = json.dumps([float(value) for value in cmpr['values']])
            context['actual_totals'] = json.dumps([float(value) for value in cma['values']])
            context['dashboard_data'] = dashboard_data

        # Personnel and Contracts totals
        personnel = Personnel.objects.filter(business_unit=self.current)
        context['personnel'] = personnel
        contracts = Contract.objects.filter(business_unit=self.current)
        context['contracts'] = contracts

        return context


class DashboardMonthView(DashboardView):
    template_name = 'accounting/dashboard_month.html'

    def get_context_data(self, **kwargs):
        context = super(DashboardMonthView, self).get_context_data(**kwargs)
        month_data = {
            'month': Month.objects.get(pk=kwargs['month']),
        }
        context['month_data'] = month_data
        index = context['months'].index(month_data['month'])

        # calculate month_values per index
        context['month_cma'] = context['cma']['values'][index]
        context['month_cmpr_pre'] = context['cmpr']['values'][index - 1]

        context['expenses'] = Expense.objects.filter(month=kwargs['month'])
        context['payrolls'] = Payroll.objects.filter(month=kwargs['month'])

        print context['expenses']

        context['month_cmpr'] = context['cmpr']['values'][index]
        context['month_ima'] = context['ima']['values'][index]
        context['month_imp'] = context['imp']['values'][index]
        print context['month_imp']
        context['month_ema'] = context['ema']['values'][index]
        context['month_emp'] = context['emp']['values'][index]
        context['month_pmp'] = context['pmp']['values'][index]
        context['month_pma'] = context['pma']['values'][index]
        context['month_tama'] = context['tama']['values'][index]
        context['month_tamp'] = context['tamp']['values'][index]

        salary = Salary.objects.filter(business_unit=self.current)
        context['salary'] = salary

        part_time = PartTime.objects.filter(business_unit=self.current)
        context['part_time'] = part_time

        # part time amounts
        part_time_hours_total = 0
        part_time_total = Decimal('0.00')

        # salary amounts
        monthly_amount = Decimal('0.00')
        social_security_total = Decimal('0.00')
        fed_health_insurance_total = Decimal('0.00')
        retirement_total = Decimal('0.00')
        medical_insurance_total = Decimal('0.00')
        staff_benefits_total = Decimal('0.00')
        fringe_total = Decimal('0.00')

        for part_time in PartTime.objects.filter(business_unit=self.current):
            part_time_hours_total += part_time.hours_work
            part_time_total += (part_time.hours_work * part_time.hourly_amount)

        # find salary totals for each type
        for salary in Salary.objects.filter(business_unit=self.current):
            monthly_amount = (salary.salary_amount / 12)
            social_security_total += salary.social_security_amount
            fed_health_insurance_total += salary.fed_health_insurance_amount
            retirement_total += salary.retirement_amount
            medical_insurance_total += salary.medical_insurance_amount
            staff_benefits_total += salary.staff_benefits_amount
            fringe_total += salary.fringe_amount

        context['ssa'] = social_security_total
        context['fhit'] = fed_health_insurance_total
        context['rt'] = retirement_total
        context['mit'] = medical_insurance_total
        context['sbt'] = staff_benefits_total
        context['ft'] = fringe_total

        context['ptht'] = part_time_hours_total
        context['ptt'] = part_time_total

        return context


class ContractsView(ViewerMixin, SetUpMixin, TemplateView):
    template_name = 'accounting/contracts.html'

    def get_context_data(self, **kwargs):
        context = super(ContractsView, self).get_context_data()
        context['business_units'] = self.business_units
        contracts = Contract.objects.filter(business_unit=self.current)
        completed_contracts = []
        active_contracts = []
        for contract in contracts:
            if contract.contract_state == 'ACTIVE':
                invoices = Invoice.objects.filter(contract=contract)
                print invoices
                active_contracts.extend([
                    {
                        'contract': contract,
                        'invoices': invoices,
                    }
                ])
            elif contract.contract_state == 'COMPLETE':
                invoices = Invoice.objects.filter(contract=contract)
                completed_contracts.extend([
                    {
                        'contract': contract,
                        'invoices': invoices,
                    }
                ])
        context['active_contracts'] = active_contracts
        context['completed_contracts'] = completed_contracts
        return context


class RevenueView(ViewerMixin, SetUpMixin, TemplateView):
    template_name = 'accounting/revenue.html'

    def get_context_data(self, **kwargs):
        context = super(RevenueView, self).get_context_data()
        context['business_units'] = self.business_units

        # contracts = Contract.objects.filter(business_unit=self.current)
        # contract_invoices = []
        # for contract in contracts:
        #     invoices = Invoice.objects.filter(contract=contract)
        #     contract_invoices.extend(
        #     [
        #         {
        #             'contract': contract,
        #             'invoices': invoices,
        #         }
        #     ]
        #     )

        invoices = Invoice.objects.filter(contract__business_unit=self.current)
        context['invoices'] = invoices
        return context


class ExpensesView(ViewerMixin, SetUpMixin, TemplateView):
    template_name = 'accounting/expenses.html'

    def get_context_data(self, **kwargs):
        context = super(ExpensesView, self).get_context_data()
        context['business_units'] = self.business_units
        context['months'] = self.months

        month_data = []

        if 'month' in self.kwargs:
            display_month = Month.objects.get(pk=self.kwargs['month'])
        else:
            display_month = self.current_month

        try:
            cash = Cash.objects.get(month=display_month)
        except ObjectDoesNotExist:
            cash = None
        month_data = {
            'month': display_month,
            'expenses': Expense.objects.filter(month=display_month),
            'incomes': Income.objects.filter(month=display_month),
            'cash': cash
        }

        context['month_data'] = month_data
        return context


class SettingsPageView(ManagerMixin, TemplateView):
    template_name = 'accounting/settings.html'

    def get_context_data(self, **kwargs):
        context = super(SettingsPageView, self).get_context_data()
        users = AccountingUser.objects.filter(business_unit=self.current)
        viewers = []
        managers = []
        for user in users:
            if user.permission == 'VIEWER':
                viewers.append(user)
            elif user.permission == 'MANAGER':
                managers.append(user)
        context['viewers'] = viewers
        context['managers'] = managers
        context['business_units'] = self.business_units

        return context


class BusinessUnitCreateView(LoginRequiredMixin, CreateView):
    template_name = 'accounting/businessunit_create_form.html'
    form_class = BusinessUnitCreateForm
    model = BusinessUnit

    def get_success_url(self):
        return reverse_lazy('accounting:home')

    def form_valid(self, form):
        response = super(BusinessUnitCreateView, self).form_valid(form)
        form.instance.user.add(self.request.user)
        AccountingUser.objects.create(user=self.request.user, business_unit=form.instance, permission='MANAGER')
        return response


class BusinessUnitDeleteView(ManagerMixin, DeleteView):
    model = BusinessUnit
    template_name_suffix = '_delete_form'

    def get_object(self):
        return BusinessUnit.objects.get(pk=self.kwargs['business_unit'])

    def get_success_url(self):
        return reverse_lazy('accounting:home')


class BusinessUnitUpdateView(ManagerMixin, UpdateView):
    template_name_suffix = '_update_form'
    form_class = BusinessUnitUpdateForm
    model = BusinessUnit

    def get_object(self):
        return BusinessUnit.objects.get(pk=self.kwargs['business_unit'])

    def get_success_url(self):
        return reverse_lazy('accounting:home')


class FiscalYearCreateView(ManagerMixin, CreateView):
    template_name = 'accounting/fiscalyear_create_form.html'
    model = FiscalYear
    form_class = FiscalYearCreateForm

    def get_success_url(self):
        return reverse_lazy('accounting:dashboard', kwargs=self.kwargs)

    def form_valid(self, form):
        business_unit = BusinessUnit.objects.get(pk=self.kwargs['business_unit'])
        form.instance.business_unit = business_unit
        response = super(FiscalYearCreateView, self).form_valid(form)
        fiscal_year = form.instance
        cash_amount = form.instance.cash_amount
        populateCashPredicted(fiscal_year=fiscal_year, cash_amount=cash_amount)
        return response


class FiscalYearDeleteView(ManagerMixin, DeleteView):
    model = FiscalYear
    template_name_suffix = '_delete_form'

    def get_object(self):
        return FiscalYear.objects.get(pk=self.kwargs['fiscal_year'])

    def get_success_url(self):
        return reverse_lazy('accounting:dashboard', kwargs={'business_unit': self.kwargs["business_unit"]})


class FiscalYearUpdateView(ManagerMixin, UpdateView):
    template_name_suffix = '_update_form'
    form_class = FiscalYearUpdateForm
    model = FiscalYear

    def get_object(self):
        return FiscalYear.objects.get(fiscal_year=self.kwargs['fiscal_year'])

    def get_success_url(self):
        return reverse_lazy('accounting:dashboard', kwargs=self.kwargs)


class ContractCreateView(ManagerMixin, CreateView):
    template_name = 'accounting/contract_create_form.html'
    model = Contract
    form_class = ContractCreateForm

    def get_success_url(self):
        return reverse_lazy('accounting:contracts', kwargs=self.kwargs)

    def form_valid(self, form):
        business_unit = BusinessUnit.objects.get(pk=self.kwargs['business_unit'])
        form.instance.business_unit = business_unit
        max_contract_number = Contract.objects.filter(business_unit=business_unit).aggregate(Max('contract_number'))
        if max_contract_number['contract_number__max'] is None:
            form.instance.contract_number = 1
        else:
            form.instance.contract_number = max_contract_number['contract_number__max'] + 1

        response = super(ContractCreateView, self).form_valid(form)
        return response


class ContractDeleteView(ManagerMixin, DeleteView):
    model = Contract
    template_name_suffix = '_delete_form'

    def get_object(self):
        return Contract.objects.get(pk=self.kwargs['contract'])

    def get_success_url(self):
        return reverse_lazy('accounting:contracts', kwargs={'business_unit': self.kwargs["business_unit"]})


class ContractUpdateView(ManagerMixin, UpdateView):
    template_name_suffix = '_update_form'
    form_class = ContractUpdateForm
    model = Contract

    def get_object(self):
        return Contract.objects.get(pk=self.kwargs['contract'])

    def get_success_url(self):
        return reverse_lazy('accounting:contracts', kwargs={'business_unit': self.kwargs["business_unit"]})


class InvoiceCreateView(ManagerMixin, CreateView):
    template_name = 'accounting/invoice_create_form.html'
    model = Invoice
    form_class = InvoiceCreateForm

    def get_success_url(self):
        return reverse_lazy('accounting:contracts', kwargs={'business_unit': self.kwargs['business_unit']})

    def form_valid(self, form):
        contract = Contract.objects.get(pk=self.kwargs['contract'])
        form.instance.contract = contract
        max_invoice_number = Invoice.objects.filter(contract=contract).aggregate(Max('number'))
        if max_invoice_number['number__max'] is None:
            form.instance.number = 1
        else:
            form.instance.number = max_invoice_number['number__max'] + 1
        form.instance.transition_state = 'NOT_INVOICED'

        business_unit = BusinessUnit.objects.get(pk=self.kwargs['business_unit'])
        form.instance.business_unit = business_unit
        month = Month.objects.get(fiscal_year__business_unit=business_unit, month__month=form.instance.date_payable.month)
        form.instance.month = month
        contract_number = str(form.instance.contract.contract_number)
        contract_number = contract_number.zfill(4)
        form.instance.name = form.instance.contract.department + contract_number + '-' + str(form.instance.number)

        response = super(InvoiceCreateView, self).form_valid(form)
        updateCashPredicted(business_unit=business_unit)
        return response


class InvoiceDeleteView(ManagerMixin, DeleteView):
    model = Invoice
    template_name_suffix = '_delete_form'

    def get_object(self):
        return Invoice.objects.get(pk=self.kwargs['invoice'])

    def get_success_url(self):
        return reverse_lazy('accounting:contracts', kwargs={'business_unit': self.kwargs["business_unit"]})

    def delete(self, request, *args, **kwargs):
        response = super(InvoiceDeleteView, self).delete(request, *args, **kwargs)
        business_unit = BusinessUnit.objects.get(pk=self.kwargs['business_unit'])
        updateCashPredicted(business_unit=business_unit)
        return response


class InvoiceUpdateView(ManagerMixin, UpdateView):
    template_name_suffix = '_update_form'
    form_class = InvoiceUpdateForm
    model = Invoice

    def get_object(self):
        return Invoice.objects.get(pk=self.kwargs['invoice'])

    def get_success_url(self):
        return reverse_lazy('accounting:contracts', kwargs={'business_unit': self.kwargs['business_unit']})

    def form_valid(self, form):
        response = super(InvoiceUpdateView, self).form_valid(form)
        business_unit = BusinessUnit.objects.get(pk=self.kwargs['business_unit'])
        updateCashPredicted(business_unit=business_unit)
        return response


class ExpenseCreateView(ManagerMixin, CreateView):
    template_name = 'accounting/expense_create_form.html'
    model = Expense
    form_class = ExpenseCreateForm

    def get_success_url(self):
        return reverse_lazy('accounting:expenses', kwargs={'business_unit': self.kwargs['business_unit'], 'month': self.kwargs['month']})

    def form_valid(self, form):
        form.instance.business_unit = BusinessUnit.objects.get(pk=self.kwargs['business_unit'])
        month = Month.objects.get(pk=self.kwargs['month'])
        try:
            if self.request.POST['reocurring']:
                months = Month.objects.filter(fiscal_year=month.fiscal_year)
                for m in months:
                    if m.month >= month.month:
                        new_date_payable = date(m.month.year, m.month.month, form.instance.date_payable.day)
                        Expense.objects.create(
                            business_unit=form.instance.business_unit,
                            month=m,
                            predicted_amount=form.instance.predicted_amount,
                            name=form.instance.name,
                            date_payable=new_date_payable,
                        )
            return redirect('accounting:expenses', pk=self.kwargs['pk'], month=self.kwargs['month'])
        except KeyError:
            print "Exception thrown"
            form.instance.month = month
        response = super(ExpenseCreateView, self).form_valid(form)
        business_unit = BusinessUnit.objects.get(pk=self.kwargs['business_unit'])
        updateCashPredicted(business_unit=business_unit)
        return response


class ExpenseDeleteView(ManagerMixin, DeleteView):
    model = Expense
    template_name_suffix = '_delete_form'

    def get_object(self):
        return Expense.objects.get(pk=self.kwargs['expense'])

    def get_success_url(self):
        return reverse_lazy('accounting:expenses', kwargs={'pk': self.kwargs["pk"], 'month': self.kwargs['month']})

    def delete(self, request, *args, **kwargs):
        response = super(ExpenseDeleteView, self).delete(request, *args, **kwargs)
        business_unit = BusinessUnit.objects.get(pk=self.kwargs['business_unit'])
        updateCashPredicted(business_unit=business_unit)
        return response


class ExpenseUpdateView(ManagerMixin, UpdateView):
    template_name_suffix = '_update_form'
    form_class = ExpenseUpdateForm
    model = Expense

    def get_object(self):
        return Expense.objects.get(pk=self.kwargs['expense'])

    def get_success_url(self):
        return reverse_lazy('accounting:expenses', kwargs={'business_unit': self.kwargs['business_unit'], 'month': self.kwargs['month']})

    def form_valid(self, form):
        response = super(ExpenseUpdateView, self).form_valid(form)
        business_unit = BusinessUnit.objects.get(pk=self.kwargs['business_unit'])
        updateCashPredicted(business_unit=business_unit)
        return response


class PersonnelView(ViewerMixin, SetUpMixin, TemplateView):
    template_name = 'accounting/personnel.html'

    def get_context_data(self, **kwargs):
        context = super(PersonnelView, self).get_context_data()
        context['business_units'] = self.business_units

        personnel = Personnel.objects.filter(business_unit=self.current)
        context['personnel'] = personnel

        salary = Salary.objects.filter(business_unit=self.current)
        context['salary'] = salary

        part_time = PartTime.objects.filter(business_unit=self.current)
        context['part_time'] = part_time

        return context


class SalaryCreateView(ManagerMixin, CreateView):
    template_name = 'accounting/salary_create_form.html'
    model = Salary
    form_class = SalaryCreateForm

    def get_success_url(self):
        return reverse_lazy('accounting:personnel', kwargs={'business_unit': self.kwargs['business_unit']})

    def form_valid(self, form):
        business_unit = BusinessUnit.objects.get(pk=self.kwargs['business_unit'])
        form.instance.business_unit = business_unit
        response = super(SalaryCreateView, self).form_valid(form)
        updatePayroll(business_unit=business_unit)
        updateCashPredicted(business_unit=business_unit)
        return response


class SalaryDeleteView(ManagerMixin, DeleteView):
    model = Salary
    template_name_suffix = '_delete_form'

    def get_object(self):
        return Salary.objects.get(pk=self.kwargs['salary'])

    def get_success_url(self):
        return reverse_lazy('accounting:personnel', kwargs={'business_unit': self.kwargs["business_unit"]})

    def delete(self, request, *args, **kwargs):
        response = super(SalaryDeleteView, self).delete(request, *args, **kwargs)
        business_unit = BusinessUnit.objects.get(pk=self.kwargs['business_unit'])
        updatePayroll(business_unit=business_unit)
        updateCashPredicted(business_unit=business_unit)
        return response


class SalaryUpdateView(ManagerMixin, UpdateView):
    template_name_suffix = '_update_form'
    form_class = SalaryUpdateForm
    model = Salary

    def get_object(self):
        return Salary.objects.get(pk=self.kwargs['salary'])

    def get_success_url(self):
        return reverse_lazy('accounting:personnel', kwargs={'business_unit': self.kwargs["business_unit"]})

    def form_valid(self, form):
        business_unit = BusinessUnit.objects.get(pk=self.kwargs['business_unit'])
        response = super(SalaryUpdateView, self).form_valid(form)
        updatePayroll(business_unit=business_unit)
        updateCashPredicted(business_unit=business_unit)
        return response


class PartTimeCreateView(ManagerMixin, CreateView):
    template_name = 'accounting/part_time_create_form.html'
    model = PartTime
    form_class = PartTimeCreateForm

    def get_context_data(self, *args, **kwargs):
        context = super(PartTimeCreateView, self).get_context_data()
        return context

    def get_success_url(self):
        return reverse_lazy('accounting:personnel', kwargs={'business_unit': self.kwargs['business_unit']})

    def form_valid(self, form):
        business_unit = BusinessUnit.objects.get(pk=self.kwargs['business_unit'])
        form.instance.business_unit = business_unit
        form.instance.hours_work = 20
        response = super(PartTimeCreateView, self).form_valid(form)
        updatePayroll(business_unit=business_unit)
        updateCashPredicted(business_unit=business_unit)
        return response


class PartTimeDeleteView(ManagerMixin, DeleteView):
    model = PartTime
    template_name = 'accounting/part_time_delete_form.html'

    def get_object(self):
        return PartTime.objects.get(pk=self.kwargs['part_time'])

    def get_success_url(self):
        return reverse_lazy('accounting:personnel', kwargs={'business_unit': self.kwargs["business_unit"]})

    def delete(self, request, *args, **kwargs):
        response = super(PartTimeDeleteView, self).delete(request, *args, **kwargs)
        business_unit = BusinessUnit.objects.get(pk=self.kwargs['business_unit'])
        updatePayroll(business_unit=business_unit)
        updateCashPredicted(business_unit=business_unit)
        return response


class PartTimeUpdateView(ManagerMixin, UpdateView):
    template_name = 'accounting/part_time_update_form.html'
    form_class = PartTimeUpdateForm
    model = PartTime

    def get_object(self):
        return PartTime.objects.get(pk=self.kwargs['part_time'])

    def get_success_url(self):
        return reverse_lazy('accounting:personnel', kwargs={'business_unit': self.kwargs['business_unit']})

    def form_valid(self, form):
        business_unit = BusinessUnit.objects.get(pk=self.kwargs['business_unit'])
        response = super(PartTimeUpdateView, self).form_valid(form)
        updatePayroll(business_unit=business_unit)
        updateCashPredicted(business_unit=business_unit)
        return response


class IncomeCreateView(ManagerMixin, CreateView):
    template_name = 'accounting/income_create_form.html'
    model = Income
    form_class = IncomeCreateForm

    def get_context_data(self, *args, **kwargs):
        context = super(IncomeCreateView, self).get_context_data()
        return context

    def get_success_url(self):
        return reverse_lazy('accounting:expenses', kwargs={'business_unit': self.kwargs['business_unit'], 'month': self.kwargs['month']})

    def form_valid(self, form):
        form.instance.business_unit = BusinessUnit.objects.get(pk=self.kwargs['business_unit'])
        month = Month.objects.get(pk=self.kwargs['month'])
        try:
            if self.request.POST['reocurring']:
                months = Month.objects.filter(fiscal_year=month.fiscal_year)
                for m in months:
                    if m.month >= month.month:
                        Income.objects.create(
                            business_unit=form.instance.business_unit,
                            month=m,
                            predicted_amount=form.instance.predicted_amount,
                            name=form.instance.name,
                            date_payable=form.instance.date_payable,
                        )
            return redirect('accounting:expenses', business_unit=self.kwargs['business_unit'], month=self.kwargs['month'])
        except KeyError:
            print "Exception thrown"
            form.instance.month = month
        response = super(IncomeCreateView, self).form_valid(form)

        return response


class IncomeDeleteView(ManagerMixin, DeleteView):
    model = Income
    template_name_suffix = '_delete_form'

    def get_object(self):
        return Income.objects.get(pk=self.kwargs['income'])

    def get_success_url(self):
        return reverse_lazy('accounting:expenses', kwargs={'business_unit': self.kwargs["business_unit"], 'month': self.kwargs['month']})

    def delete(self, request, *args, **kwargs):
        response = super(IncomeDeleteView, self).delete(request, *args, **kwargs)
        business_unit = BusinessUnit.objects.get(pk=self.kwargs['business_unit'])
        updateCashPredicted(business_unit=business_unit)
        return response


class IncomeUpdateView(ManagerMixin, UpdateView):
    template_name_suffix = '_update_form'
    form_class = IncomeUpdateForm
    model = Income

    def get_object(self):
        return Income.objects.get(pk=self.kwargs['income'])

    def get_success_url(self):
        return reverse_lazy('accounting:expenses', kwargs={'business_unit': self.kwargs['business_unit'], 'month': self.kwargs['month']})

    def form_valid(self, form):
        business_unit = BusinessUnit.objects.get(pk=self.kwargs['business_unit'])
        response = super(IncomeUpdateView, self).form_valid(form)
        updateCashPredicted(business_unit=business_unit)
        return response


class CashUpdateView(ManagerMixin, UpdateView):
    template_name_suffix = '_update_form'
    form_class = CashUpdateForm
    model = Cash

    def get_object(self):
        return Cash.objects.get(pk=self.kwargs['cash'])

    def get_success_url(self):
        return reverse_lazy('accounting:expenses', kwargs={'business_unit': self.kwargs['business_unit'], 'month': self.kwargs['month']})

    def form_valid(self, form):
        business_unit = BusinessUnit.objects.get(pk=self.kwargs['business_unit'])
        response = super(CashUpdateView, self).form_valid(form)
        updateCashPredicted(business_unit=business_unit)
        return response


class AccountingUserCreateView(ManagerMixin, CreateView):
    template_name = 'accounting/accounting_user_create_form.html'
    model = AccountingUser
    form_class = AccountingUserCreateForm

    def get_success_url(self):
        return reverse_lazy('accounting:settings', kwargs={'business_unit': self.kwargs['business_unit']})

    def form_valid(self, form):
        business_unit = BusinessUnit.objects.get(pk=self.kwargs['business_unit'])
        form.instance.business_unit = business_unit
        form.instance.hours_work = 20
        response = super(AccountingUserCreateView, self).form_valid(form)
        updatePayroll(business_unit=business_unit)
        updateCashPredicted(business_unit=business_unit)
        return response


class AccountingUserDeleteView(ManagerMixin, DeleteView):
    model = AccountingUser
    template_name = 'accounting/accounting_user_delete_form.html'

    def get_object(self):
        return AccountingUser.objects.get(pk=self.kwargs['accounting_user'])

    def get_success_url(self):
        return reverse_lazy('accounting:settings', kwargs={'business_unit': self.kwargs["business_unit"]})


class AccountingUserUpdateView(ManagerMixin, UpdateView):
    template_name = 'accounting/accounting_user_update_form.html'
    form_class = AccountingUserUpdateForm
    model = AccountingUser

    def get_object(self):
        return AccountingUser.objects.get(pk=self.kwargs['accounting_user'])

    def get_success_url(self):
        return reverse_lazy('accounting:settings', kwargs={'business_unit': self.kwargs['business_unit']})


def updatePayroll(business_unit):
    # for personnel in business unit
    # total up salary
    # total up part time
    payroll_amount = Decimal('0.00')
    salary = Salary.objects.filter(business_unit=business_unit)
    for salary in salary:
        payroll_amount += ((salary.salary_amount / 12) + salary.social_security_amount + salary.fed_health_insurance_amount + salary.retirement_amount + salary.medical_insurance_amount + salary.staff_benefits_amount + salary.fringe_amount)
    part_time = PartTime.objects.filter(business_unit=business_unit)
    for part_time in part_time:
        payroll_amount += part_time.hourly_amount * part_time.hours_work

    # for month in month in fiscal year
    # get payroll object
    # if payroll object expese is not reconciled
    # update its predicted value with the total
    fiscal_years = FiscalYear.objects.filter(business_unit=business_unit)
    for fiscal_year in fiscal_years:
        months = Month.objects.filter(fiscal_year=fiscal_year)
        for month in months:
            payroll = None
            try:
                payroll = Payroll.objects.get(month=month)
            except ObjectDoesNotExist:
                expense = Expense.objects.create(
                    business_unit=business_unit,
                    month=month,
                    name='Payroll',
                    date_payable=month.month
                )
                payroll = Payroll.objects.create(month=month, expense=expense)
            payroll.expense.predicted_amount = payroll_amount
            payroll.expense.save()


def populateCashPredicted(fiscal_year, cash_amount):
    cash_previous = Decimal(cash_amount)
    for month in Month.objects.filter(fiscal_year=fiscal_year):
        expense_month_projected = Decimal('0.00')
        for expense in Expense.objects.filter(month=month):
            expense_month_projected += expense.predicted_amount
        income_month_projected = Decimal('0.00')
        for income in Income.objects.filter(month=month):
            income_month_projected += income.predicted_amount
        cash = Cash.objects.get(month=month)

        cash.predicted_amount = cash_previous - expense_month_projected + income_month_projected
        cash.save()
        if cash.reconciled:
            cash_previous = cash.actual_amount
        else:
            cash_previous = cash.predicted_amount


def updateCashPredicted(business_unit):
    fiscal_years = FiscalYear.objects.filter(business_unit=business_unit)
    for fiscal_year in fiscal_years:
        cash_previous = Decimal(fiscal_year.cash_amount)
        for month in Month.objects.filter(fiscal_year=fiscal_year):
            expense_month_projected = Decimal('0.00')
            for expense in Expense.objects.filter(month=month):
                expense_month_projected += expense.predicted_amount
            income_month_projected = Decimal('0.00')
            for income in Income.objects.filter(month=month):
                income_month_projected += income.predicted_amount
            cash = Cash.objects.get(month=month)
            cash.predicted_amount = cash_previous - expense_month_projected + income_month_projected
            cash.save()
            if cash.reconciled:
                cash_previous = cash.actual_amount
            else:
                cash_previous = cash.predicted_amount
