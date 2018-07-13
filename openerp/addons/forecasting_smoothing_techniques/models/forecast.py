# coding: utf-8
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: Katherine Zaoral <kathy@vauxoo.com>
#    planned by: Nhomar Hernandez <nhomar@vauxoo.com>
#                Gabriela Quilarque <gabriela@vauxoo.com>
############################################################################

from __future__ import division

import logging

from openerp import _, api, fields, models
from openerp.exceptions import ValidationError

_logger = logging.getLogger(__name__)

try:
    import pandas as pd
except ImportError:
    _logger.debug('Cannot `import pandas`.')


class ForecastData(models.Model):
    _name = 'forecast.data'
    _description = 'Forecast Data'
    _rec_name = 'sequence'

    @api.model
    def _default_forecast(self):
        forecast_id = self._context.get('forecast_id', False)
        return forecast_id

    sequence = fields.Integer(
        help="Position in the list regarding this list and this forecast",
        default=10)
    label = fields.Char()
    value = fields.Float()
    forecast_id = fields.Many2one(
        'forecast',
        required=True,
        default=_default_forecast,
        help="Forecast which this data is related to")

    sma = fields.Float(
        'SMA', help="Simple Moving Average Forcasting (SMA)")
    sma_error = fields.Float(
        'SMA MA Error', help="Mean Absolute Error for SMA")
    cma = fields.Float(
        'CMA', help="Cumulative Moving Average Forcasting (CMA)")
    cma_error = fields.Float(
        'CMA MA Error', help="Mean Absolute Error for CMA")
    wma = fields.Float(
        'WMA', help="Weighted Moving Average Forecasting (WMA)")
    wma_error = fields.Float(
        'WMA MA Error', help="Mean Absolute Error for WMA")
    es1 = fields.Float(
        'ES1', help="Single Exponential Smoothing (ES1)")
    es1_error = fields.Float(
        'ES1 MA Error', help="Mean Absolute Error for ES1")
    es2 = fields.Float(
        'ES2', help="Double Exponential Smoothing (ES2)")
    es2_error = fields.Float(
        'ES2 MA Error', help="Mean Absolute Error for ES2")
    es3 = fields.Float(
        'ES3', help="Triple Exponential Smoothing (ES3)")
    es3_error = fields.Float(
        'ES3 MA Error', help="Mean Absolute Error for ES3")
    holt = fields.Float(
        'HOLT', help="Holt's Linear Smoothing (HOLT)")
    holt_error = fields.Float(
        'HOLT MA Error', help="Mean Absolute Error for HOLT")
    holt_level = fields.Float(
        'HOLT LEVEL', help="Holt's Linear Smoothing Level function")
    holt_trend = fields.Float(
        'HOLT TREND', help="Holt's Linear Smoothing Trend function")

    _sql_constraints = [
        ('sequence_uniq', 'unique(sequence, forecast_id)',
            'Several sequences with the same value do not make sense yet!'),
    ]


class Forecast(models.Model):

    _name = 'forecast'
    _description = 'Forecast'
    _inherit = ['mail.thread']

    name = fields.Char(
        help='Name given by the user to quick reference the forecasting')

    value_ids = fields.One2many(
        'forecast.data',
        'forecast_id',
        string='Values',
        copy=False,
        help='List of values to be used to compute this forecast')

    # Moving Average
    period = fields.Integer(
        'Period', default=5, help="Moving Average Period")

    # Simple Moving Average
    sma_forecast = fields.Float(
        'Forecast',
        compute='_compute_sma',
        help="Simple Moving Average Forcasting (SMA)"
    )
    sma_ma_error = fields.Float(
        'MA Error',
        compute='_compute_sma',
        help="Mean Absolute Error for SMA"
    )
    sma_warning = fields.Char('SMA WARNING')

    # Cumulative Moving Average
    cma_forecast = fields.Float(
        'Forecast',
        compute='_compute_cma',
        help="Cumulative Moving Average Forcasting (CMA)"
    )
    cma_ma_error = fields.Float(
        'MA Error',
        compute='_compute_cma',
        help="Mean Absolute Error for CMA"
    )
    cma_warning = fields.Char('CMA WARNING')

    # Weighted Moving Average
    wma_forecast = fields.Float(
        'Forecast',
        compute='_compute_wma',
        help="Weighted Moving Average Forecasting (WMA)"
    )
    wma_ma_error = fields.Float(
        'MA Error',
        compute='_compute_wma',
        help="Mean Absolute Error for WMA"
    )
    wma_warning = fields.Char('WMA WARNING')

    # Single, Double, & Triple Exponential Smoothing
    exp_alpha = fields.Float(
        'Alpha', default=0.3,
        help='Exponential Alpha. A small alpha provides a detectable and'
             ' visible smoothing. While a large alpha provides a fast'
             ' response to the recent changes in the time series but'
             ' provides a smaller amount of smoothing')

    single_forecast = fields.Float(
        'Forecast',
        compute='_compute_exp',
        help="Single Exponential Smoothing (SES)"
    )
    single_ma_error = fields.Float(
        'MA Error',
        compute='_compute_exp',
        help="Mean Absolute Error for SES"
    )
    double_forecast = fields.Float(
        'Forecast',
        compute='_compute_exp',
        help="Double Exponential Smoothing (DES)"
    )
    double_ma_error = fields.Float(
        'MA Error',
        compute='_compute_exp',
        help="Mean Absolute Error for DES"
    )
    triple_forecast = fields.Float(
        'Forecast',
        compute='_compute_exp',
        help="Triple Exponential Smoothing (TES)"
    )
    triple_ma_error = fields.Float(
        'MA Error',
        compute='_compute_exp',
        help="Mean Absolute Error for TES"
    )
    exp_warning = fields.Char('EXP WARNING')

    # Holt's Linear Smoothing
    holt_alpha = fields.Float(
        'Alpha', default=0.3,
        help="Holt's Alpha Parameter"
    )
    beta = fields.Float(
        'Beta', default=0.03,
        help="Holt's Beta Parameter"
    )
    holt_period = fields.Float(
        "Holt's Period", default=1,
        help="Forecasting K periods into the future to calculate Holt's"
             " Linear Smoothing")
    holt_forecast = fields.Float(
        'Forecast',
        compute='_compute_holt',
        help="Holt's Linear Smoothing (HOLT)"
    )
    holt_ma_error = fields.Float(
        'MA Error',
        compute='_compute_holt',
        help="Mean Absolute Error for HOLT"
    )
    holt_warning = fields.Char('HOLT WARNING')

    mhelp = fields.Boolean(
        'Show Mathematic Base Help',
        help='Allows you to show the mathematic base help in the form view')

    shelp = fields.Boolean(
        'Show Help', help='Allows you to show the help in the form view')

    @api.constrains('period')
    def _check_period(self):
        """ Check that the period to make the move average forcasting is at
        least greather than one. If not, there is not way to calculate the
        average.
        """
        if self.period <= 1:
            raise ValidationError(
                _("Period must be an integer greater than 1."))

    @api.constrains('exp_alpha')
    def _check_exp_alpha(self):
        """ Check that the alpha used to calculate exponential smoothing
        forecasting is a value between 0 and 1 thus is specificated in the
        exponential smoothing method rules.
        """
        if self.exp_alpha <= 0 or self.exp_alpha >= 1:
            raise ValidationError(_("Alpha should be between 0 and 1."))

    @api.constrains('holt_alpha')
    def _check_holt_alpha(self):
        """ Check that the alpha used to calculate holt linear smoothing
        forecasting is a value between 0 and 1 thus is specificated in the
        holt linear smoothing method rules.
        """
        if self.holt_alpha <= 0 or self.holt_alpha >= 1:
            raise ValidationError(_("Alpha should be between 0 and 1."))

    @api.constrains('beta')
    def _check_beta(self):
        """ Check that the beta used to calculate holt linear smoothing
        forecasting is a value between 0 and 1 thus is specificated in the
        holt linear smoothing method rules.
        """
        if self.beta <= 0 or self.beta >= 1:
            raise ValidationError(_("Beta should be between 0 and 1."))

    @api.multi
    def reset_defaults(self):
        """ Reset defaults for the variables used in the current calc.
        ['period', 'exp_alpha', 'holt_alpha', 'beta', 'holt_period']

        This is used in a button called Reset Defaults in the
        forecast form view.

        :return: True
        """
        parameter_fields = [
            'period', 'exp_alpha', 'holt_alpha', 'beta', 'holt_period']
        defaults = self.default_get(parameter_fields)
        self.write(defaults)

    @api.multi
    def clear(self):
        """ Clear all the forecast data fields.

        This is used in a button called Clear in the
        forecast form view.

        :return: True
        """
        self.write({
            'value_ids': [(2, value.id) for value in self.value_ids]})

    @api.model
    def get_value_ids_dict(self, data):
        """ Transform the pandas.DataFrame object to a list of values to be
        written as a o2m field in odoo named value_ids.

        :data: DataFrame object with the forecasting results per point

        :returns: list with the values to update the o2m forecast.value_ids
        field
        """
        value_ids = list()
        data.fillna(0.0, inplace=True)
        for index in range(1, len(data) + 1):
            new_values = data.loc[index].to_dict()
            new_values.pop('value')
            value_ids.append((1, int(new_values.pop('id')), new_values))
        return value_ids

    @api.multi
    def get_values_dataframe(self, forecast_cols):
        """ Transform forecasting data into a pandas.DataFrame object to be use
        to calculate the forecastings.

        By default the ['id', 'value', 'sequence'] forecast data fields are
        added to DataFrame object by default. The user can add another
        parameter forecast_cols to indicate the name of the columns that want
        to add the the DataFrame object to save the forcasting calculation
        values.

        :forecast_cols: list of columns to add to the DataFrame (this columns
        are mean to be used to save the forecasting calculation) By example
        the simple moving averga (sma) add two columns sma and sma_error to
        save the forecasting and the absolute mean error.

        :returns: DataFrame object with the datas value.
        """
        values = []
        for value in self.env['forecast'].browse(self._ids).value_ids:
            values.append(
                {'id': value.id,
                 'label': value.label,
                 'value': value.value,
                 'sequence': value.sequence})
        cols = ['id', 'value', 'sequence'] + forecast_cols
        data = pd.DataFrame(values, columns=cols)
        data.set_index('sequence', inplace=True)
        return data

    @api.model
    def almost_equal(self, actual, expected):
        """ Compare two values: actual and expected one and check if there are
        close enoght to consider as equals.

        :actual: real value of the forecasting (float number)
        :expected: expected value of the forecasting (float or int number)

        :returns: True if the actual and expected values are almost equal
        False if not.
        """
        vdiff = abs(actual - float(expected))
        allowed_error = 2
        if int(round(vdiff)) <= allowed_error:
            return True
        return False

    def minimun_data(self, nvalues, minimum, warning_field):
        """ Check is the is forecast data and if the data is  at least the
        minimum to calculate the forecast. If not will write an error over the
        correspond forecast method warning field.

        :nvalues: length of the forecast data list
        :minimum: value to compare the values
        :warning_field: warning field to write the non enough data.

        :return: True if minimum data, False if not enough
        """
        error = (_('Not not enough data to calculate forecast method') +
                 ' >= ' + str(minimum))
        error = error.format(fst=warning_field.split('_')[0].upper())

        if not nvalues:
            return False
        elif nvalues < minimum:
            self.write({warning_field: error})
            return False
        else:
            return True

    @api.depends('period')
    def _compute_cma(self):
        """ This method calculate the CUMULATIVE MOVING AVERAGE forecasting
        smoothing method (CMA) and Mean Absolute error.

        Update the forecast fields ['cma_forecast', 'cma_ma_error']  and the
        forecast values ['cma', 'cma_error']
        """
        for forecast in self.env['forecast'].browse(self._ids):

            # Get basic parameters to calculate
            period = forecast.period
            # TODO evaluate the way that the cache is working here.
            values = forecast.value_ids

            # Check minimum data
            if not forecast.minimun_data(len(values), period, 'cma_warning'):
                continue

            # Transform value data to Dataframe pandas object
            data = forecast.get_values_dataframe(['cma', 'cma_error'])

            # Calculate Forecasting for the other points
            for index in range(period, len(data) + 1):
                value_set = data[:index].tail(period)
                cma = value_set.value.sum() / float(period)
                data.at[index, 'cma'] = cma

            # Calculate mean errors
            # TODO can be improve using mean() method
            data = data.assign(
                cma_error=lambda x: abs(x.cma - x.value),
            )

            # Save global results
            cma_forecast = cma
            cma_ma_error = data.cma_error.sum() / data.cma.count()

            # Save individual values results
            value_ids = forecast.get_value_ids_dict(data)

            # Write values
            forecast.cma_forecast = cma_forecast
            forecast.cma_ma_error = cma_ma_error
            forecast.write({'value_ids': value_ids})

    @api.depends('period')
    def _compute_sma(self):
        """ This method calculate the SIMPLE MOVING AVERAGE forecasting
        smoothing method (SMA) and Mean Absolute error.

        Update the forecast fields ['sma_forecast', 'sma_ma_error']  and the
        forecast values ['sma', 'sma_error']
        """
        for forecast in self.env['forecast'].browse(self._ids):
            # Get basic parameters to calculate
            values = forecast.value_ids
            period = forecast.period

            # Check minimum data
            if not forecast.minimun_data(len(values), period + 1,
                                         'sma_warning'):
                continue

            # Transform value data to Dataframe pandas object
            data = forecast.get_values_dataframe(['sma', 'sma_error'])

            # Calculate Forecasting for the other points
            for index in range(period + 1, len(data) + 1):
                value_set = data[:index - 1].tail(period)
                sma = value_set.value.sum() / float(period)
                data.at[index, 'sma'] = sma

            # Calculate mean errors
            # TODO can be improve using mean() method
            data = data.assign(
                sma_error=lambda x: abs(x.sma - x.value),
            )

            # Save global results
            sma_forecast = sma
            sma_ma_error = data.sma_error.sum() / data.sma.count()

            # Save individual values results
            value_ids = forecast.get_value_ids_dict(data)

            # Write values
            forecast.sma_forecast = sma_forecast
            forecast.sma_ma_error = sma_ma_error
            forecast.write({'value_ids': value_ids})

    @api.depends('period')
    def _compute_wma(self):
        """ This method calculate the WEIGHTED MOVING AVERAGE forecasting
        smoothing method (WMA) and Mean Absolute error.

        Update the forecast fields ['wma_forecast', 'wma_ma_error']  and the
        forecast values ['wma', 'wma_error']
        """
        for forecast in self.env['forecast'].browse(self._ids):
            # Get basic parameters to calculate
            values = forecast.value_ids
            period = forecast.period

            # Check minimum data
            if not forecast.minimun_data(len(values), period, 'wma_warning'):
                continue

            # Transform value data to Dataframe pandas object
            data = forecast.get_values_dataframe(['wma', 'wma_error'])

            weight = (float(period) * (float(period) + 1.0)) / 2.0

            # Calculate Forecasting for the other points
            for index in range(period, len(data) + 1):
                value_set = data[:index].tail(period)
                wma = sum([
                    ((day) / weight) * value
                    for (day, value) in enumerate(value_set.value.values, 1)])
                data.at[index, 'wma'] = wma

            # Calculate mean errors
            # TODO can be improve using mean() method
            data = data.assign(
                wma_error=lambda x: abs(x.wma - x.value),
            )

            # Save global results
            wma_forecast = wma
            wma_ma_error = data.wma_error.sum() / data.wma.count()

            # Save individual values results
            value_ids = forecast.get_value_ids_dict(data)

            # Write values
            forecast.wma_forecast = wma_forecast
            forecast.wma_ma_error = wma_ma_error
            forecast.write({'value_ids': value_ids})

    @api.depends('exp_alpha')
    def _compute_exp(self):
        """ This method calculate the SINGLE, DOUBLE, & TRIPLE EXPONENTIAL
        SMOOTHING forecasting method (ES1, ES2, ES3) and
        Mean Absolute error for each forecast result.

        Update the forecast fields [
            'single_forecast', 'single_ma_error',
            'double_forecast', 'double_ma_error',
            'triple_forecast', 'triple_ma_error' ]
        and the forecast values [
            'es1', 'es1_error',
            'es2', 'es2_error',
            'es3', 'es3_error' ]
            ]
        """
        for forecast in self.env['forecast'].browse(self._ids):
            # Get basic parameters to calculate
            values = forecast.value_ids
            alpha = forecast.exp_alpha

            # Check minimum data
            if not forecast.minimun_data(len(values), 2, 'exp_warning'):
                continue

            # Transform value data to Dataframe pandas object
            data = forecast.get_values_dataframe(
                ['es1', 'es1_error',
                 'es2', 'es2_error',
                 'es3', 'es3_error'])

            # Calculate Forecasting per first point
            val1 = data.loc[2].value
            data[:1] = data.query('sequence == 1').assign(
                es1=val1, es2=val1, es3=val1)

            # Calculate Forecasting for the other points
            for index in range(2, len(data) + 1):
                value = data.loc[index].value
                last_item = data.loc[index - 1]
                es1 = alpha * value + (1.0 - alpha) * last_item.es1
                es2 = alpha * es1 + (1.0 - alpha) * last_item.es2
                es3 = alpha * es2 + (1.0 - alpha) * last_item.es3
                data.at[index, 'es1'] = es1
                data.at[index, 'es2'] = es2
                data.at[index, 'es3'] = es3

            # Calculate mean errors
            # TODO can be improve using mean() method
            data = data.assign(
                es1_error=lambda x: abs(x.es1 - x.value),
                es2_error=lambda x: abs(x.es2 - x.value),
                es3_error=lambda x: abs(x.es3 - x.value),
            )

            # Save global results
            last = data.tail(1).iloc[-1]
            a2 = 2.0 * last.es1 - last.es2
            b2 = (alpha / (1.0 - alpha)) * (last.es1 - last.es2)
            a3 = 3.0 * last.es1 - 3.0 * last.es2 + last.es3
            b3 = ((alpha / (2.0 * pow(1.0 - alpha, 2.0))) * (
                (6.0 - 5.0 * alpha) * last.es1 -
                (10.0 - 8.0 * alpha) * last.es2 +
                (4.0 - 3.0 * alpha) * last.es3))
            c3 = (pow((alpha / (1.0 - alpha)), 2.0) *
                  (last.es1 - 2.0 * last.es2 + last.es3))
            single_forecast = last.es1
            double_forecast = a2 + b2
            triple_forecast = a3 + b3 + 0.5 * c3
            single_ma_error = data.es1_error.sum() / len(data)
            double_ma_error = data.es2_error.sum() / len(data)
            triple_ma_error = data.es3_error.sum() / len(data)

            # Save individual values results
            value_ids = forecast.get_value_ids_dict(data)

            # Write values
            forecast.single_forecast = single_forecast
            forecast.double_forecast = double_forecast
            forecast.triple_forecast = triple_forecast
            forecast.single_ma_error = single_ma_error
            forecast.double_ma_error = double_ma_error
            forecast.triple_ma_error = triple_ma_error
            forecast.write({'value_ids': value_ids})

    @api.depends('holt_alpha', 'beta', 'holt_period')
    def _compute_holt(self):
        """ This method calculate the HOLT'S LINEAR SMOOTHING forecasting
        smoothing method (HOLT) and Mean Absolute error.

        Update the forecast fields ['holt_forecast', 'holt_ma_error'] and the
        forecast values ['holt', 'holt_error', 'holt_level', 'holt_trend']
        """
        for forecast in self.env['forecast'].browse(self._ids):
            # Get basic parameters to make the forecasting calculation
            values = forecast.value_ids
            alpha = forecast.holt_alpha
            beta = forecast.beta
            period = forecast.holt_period

            # Check minimum data
            if not forecast.minimun_data(len(values), 3, 'holt_warning'):
                continue

            # Transform value data to pandas.Dataframe object
            data = forecast.get_values_dataframe([
                'holt', 'holt_level', 'holt_trend', 'holt_error'])

            # NOTE: Forecasting first point do not exist for this forcasting

            # Calculate Forecasting second point
            holt_level = data.loc[2].value,
            holt_trend = data.loc[2].value - data.loc[1].value,

            data[1:2] = data.query('sequence == 2').assign(
                holt_level=holt_level, holt_trend=holt_trend)

            # Calculate Forecasting for the other 2+n points
            for index in range(3, len(data) + 1):
                value = data.loc[index].value
                prev = data.loc[index - 1]
                holt_func = prev.holt_level + prev.holt_trend
                holt_level = alpha * value + (1.0 - alpha) * holt_func
                holt_trend = (
                    beta * (holt_level - prev.holt_level) + (1.0 - beta) *
                    prev.holt_trend)
                data.at[index, 'holt'] = holt_func
                data.at[index, 'holt_level'] = holt_level
                data.at[index, 'holt_trend'] = holt_trend

            # Calculate mean error
            # TODO can be improve using mean() method?
            data = data.assign(holt_error=lambda x: abs(x.holt - x.value))

            # Save global results
            last = data.tail(1).iloc[-1]
            holt_forecast = last.holt_level + period * last.holt_trend
            holt_ma_error = data.holt_error.sum() / (len(data) - 3.0)

            # Save individual values results
            value_ids = forecast.get_value_ids_dict(data)

            # Write values
            forecast.holt_forecast = holt_forecast
            forecast.holt_ma_error = holt_ma_error
            forecast.write({'value_ids': value_ids})
