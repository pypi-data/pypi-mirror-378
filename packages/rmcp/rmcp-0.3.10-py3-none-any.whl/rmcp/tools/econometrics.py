"""
Econometric analysis tools for RMCP.
Advanced econometric modeling for panel data, instrumental variables, etc.
"""

from typing import Any

from ..core.schemas import formula_schema, table_schema
from ..r_integration import execute_r_script_async
from ..registries.tools import tool


@tool(
    name="panel_regression",
    input_schema={
        "type": "object",
        "properties": {
            "data": table_schema(),
            "formula": formula_schema(),
            "id_variable": {"type": "string"},
            "time_variable": {"type": "string"},
            "model": {
                "type": "string",
                "enum": ["pooling", "within", "between", "random"],
                "default": "within",
            },
            "robust": {"type": "boolean", "default": True},
        },
        "required": ["data", "formula", "id_variable", "time_variable"],
    },
    output_schema={
        "type": "object",
        "properties": {
            "coefficients": {
                "type": "object",
                "description": "Estimated coefficients",
                "additionalProperties": {"type": "number"},
            },
            "std_errors": {
                "type": "object",
                "description": "Standard errors of coefficients",
                "additionalProperties": {"type": "number"},
            },
            "t_values": {
                "type": "object",
                "description": "t-statistics for coefficients",
                "additionalProperties": {"type": "number"},
            },
            "p_values": {
                "type": "object",
                "description": "P-values for coefficient significance tests",
                "additionalProperties": {"type": "number"},
            },
            "r_squared": {
                "type": "number",
                "description": "R-squared (overall fit)",
                "minimum": 0,
                "maximum": 1,
            },
            "adj_r_squared": {
                "type": "number",
                "description": "Adjusted R-squared",
                "maximum": 1,
            },
            "model_type": {
                "type": "string",
                "enum": ["pooling", "within", "between", "random"],
                "description": "Type of panel model estimated",
            },
            "robust_se": {
                "type": "boolean",
                "description": "Whether robust standard errors were used",
            },
            "n_obs": {
                "type": "integer",
                "description": "Total number of observations",
                "minimum": 1,
            },
            "n_groups": {
                "type": "integer",
                "description": "Number of cross-sectional units",
                "minimum": 1,
            },
            "time_periods": {
                "type": "integer",
                "description": "Number of time periods",
                "minimum": 1,
            },
            "formula": {"type": "string", "description": "Model formula used"},
            "id_variable": {
                "type": "string",
                "description": "Cross-sectional identifier variable",
            },
            "time_variable": {
                "type": "string",
                "description": "Time identifier variable",
            },
        },
        "required": [
            "coefficients",
            "std_errors",
            "t_values",
            "p_values",
            "r_squared",
            "adj_r_squared",
            "model_type",
            "robust_se",
            "n_obs",
            "n_groups",
            "time_periods",
            "formula",
            "id_variable",
            "time_variable",
        ],
        "additionalProperties": False,
    },
    description="Panel data regression with fixed/random effects",
)
async def panel_regression(context, params) -> dict[str, Any]:
    """Perform panel data regression."""
    await context.info("Fitting panel data regression")
    r_script = """
    library(plm)
    data <- as.data.frame(args$data)
    formula <- as.formula(args$formula)
    id_var <- args$id_variable
    time_var <- args$time_variable
    model_type <- args$model %||% "within"
    robust <- args$robust %||% TRUE
    # Create panel data frame
    pdata <- pdata.frame(data, index = c(id_var, time_var))
    # Fit panel model
    if (model_type == "pooling") {
        model <- plm(formula, data = pdata, model = "pooling")
    } else if (model_type == "within") {
        model <- plm(formula, data = pdata, model = "within")  # Fixed effects
    } else if (model_type == "between") {
        model <- plm(formula, data = pdata, model = "between")
    } else if (model_type == "random") {
        model <- plm(formula, data = pdata, model = "random")
    }
    # Get robust standard errors if requested
    if (robust) {
        library(lmtest)
        robust_se <- coeftest(model, vcov = vcovHC(model, type = "HC1"))
        coef_table <- robust_se
    } else {
        coef_table <- summary(model)$coefficients
    }
    # Extract coefficients with proper names
    coef_vals <- coef_table[, "Estimate"]
    names(coef_vals) <- rownames(coef_table)
    std_err_vals <- coef_table[, "Std. Error"]
    names(std_err_vals) <- rownames(coef_table)
    t_vals <- coef_table[, "t value"]
    names(t_vals) <- rownames(coef_table)
    p_vals <- coef_table[, "Pr(>|t|)"]
    names(p_vals) <- rownames(coef_table)
    result <- list(
        coefficients = as.list(coef_vals),
        std_errors = as.list(std_err_vals),
        t_values = as.list(t_vals),
        p_values = as.list(p_vals),
        r_squared = summary(model)$r.squared[1],
        adj_r_squared = summary(model)$r.squared[2],
        model_type = model_type,
        robust_se = robust,
        n_obs = nobs(model),
        n_groups = pdim(model)$nT$n,
        time_periods = pdim(model)$nT$T,
        formula = deparse(formula),
        id_variable = id_var,
        time_variable = time_var
    )
    """
    try:
        result = await execute_r_script_async(r_script, params)
        await context.info("Panel regression completed successfully")
        return result
    except Exception as e:
        await context.error("Panel regression failed", error=str(e))
        raise


@tool(
    name="instrumental_variables",
    input_schema={
        "type": "object",
        "properties": {
            "data": table_schema(),
            "formula": {
                "type": "string",
                "description": "Format: 'y ~ x1 + x2 | z1 + z2' where | separates instruments",
            },
            "robust": {"type": "boolean", "default": True},
        },
        "required": ["data", "formula"],
    },
    output_schema={
        "type": "object",
        "properties": {
            "coefficients": {
                "type": "object",
                "description": "2SLS coefficient estimates",
                "additionalProperties": {"type": "number"},
            },
            "std_errors": {
                "type": "object",
                "description": "Standard errors of coefficients",
                "additionalProperties": {"type": "number"},
            },
            "t_values": {
                "type": "object",
                "description": "t-statistics for coefficients",
                "additionalProperties": {"type": "number"},
            },
            "p_values": {
                "type": "object",
                "description": "P-values for coefficient significance tests",
                "additionalProperties": {"type": "number"},
            },
            "r_squared": {
                "type": "number",
                "description": "R-squared value",
                "maximum": 1,
            },
            "adj_r_squared": {
                "type": "number",
                "description": "Adjusted R-squared value",
                "maximum": 1,
            },
            "weak_instruments": {
                "type": "object",
                "properties": {
                    "statistic": {
                        "type": "number",
                        "description": "Weak instruments test statistic",
                    },
                    "p_value": {
                        "type": "number",
                        "minimum": 0,
                        "maximum": 1,
                        "description": "P-value for weak instruments test",
                    },
                },
                "description": "Test for weak instruments",
            },
            "wu_hausman": {
                "type": "object",
                "properties": {
                    "statistic": {
                        "type": "number",
                        "description": "Wu-Hausman test statistic",
                    },
                    "p_value": {
                        "type": "number",
                        "minimum": 0,
                        "maximum": 1,
                        "description": "P-value for Wu-Hausman test",
                    },
                },
                "description": "Test for endogeneity",
            },
            "sargan": {
                "type": "object",
                "properties": {
                    "statistic": {
                        "type": "number",
                        "description": "Sargan test statistic",
                    },
                    "p_value": {
                        "type": "number",
                        "minimum": 0,
                        "maximum": 1,
                        "description": "P-value for Sargan test",
                    },
                },
                "description": "Test for overidentifying restrictions",
            },
            "robust_se": {
                "type": "boolean",
                "description": "Whether robust standard errors were used",
            },
            "formula": {"type": "string", "description": "IV regression formula used"},
            "n_obs": {
                "type": "integer",
                "description": "Number of observations",
                "minimum": 1,
            },
        },
        "required": [
            "coefficients",
            "std_errors",
            "t_values",
            "p_values",
            "r_squared",
            "adj_r_squared",
            "weak_instruments",
            "wu_hausman",
            "sargan",
            "robust_se",
            "formula",
            "n_obs",
        ],
        "additionalProperties": False,
    },
    description="Two-stage least squares (2SLS) instrumental variables regression",
)
async def instrumental_variables(context, params) -> dict[str, Any]:
    """Perform instrumental variables regression."""
    await context.info("Fitting instrumental variables model")
    r_script = """
    library(AER)
    data <- as.data.frame(args$data)
    formula_str <- args$formula
    robust <- args$robust %||% TRUE
    # Parse IV formula (y ~ x1 + x2 | z1 + z2)
    formula <- as.formula(formula_str)
    # Fit 2SLS model
    iv_model <- ivreg(formula, data = data)
    # Get robust standard errors if requested
    if (robust) {
        robust_se <- coeftest(iv_model, vcov = sandwich)
        coef_table <- robust_se
    } else {
        coef_table <- summary(iv_model)$coefficients
    }
    # Diagnostic tests
    summary_iv <- summary(iv_model, diagnostics = TRUE)
    # Extract coefficients with proper names
    coef_vals <- coef_table[, "Estimate"]
    names(coef_vals) <- rownames(coef_table)
    std_err_vals <- coef_table[, "Std. Error"]
    names(std_err_vals) <- rownames(coef_table)
    t_vals <- coef_table[, "t value"]
    names(t_vals) <- rownames(coef_table)
    p_vals <- coef_table[, "Pr(>|t|)"]
    names(p_vals) <- rownames(coef_table)
    result <- list(
        coefficients = as.list(coef_vals),
        std_errors = as.list(std_err_vals),
        t_values = as.list(t_vals),
        p_values = as.list(p_vals),
        r_squared = summary_iv$r.squared,
        adj_r_squared = summary_iv$adj.r.squared,
        weak_instruments = {
            wi_stat <- if (is.na(summary_iv$diagnostics["Weak instruments", "statistic"])) NULL else summary_iv$diagnostics["Weak instruments", "statistic"]
            wi_p <- if (is.na(summary_iv$diagnostics["Weak instruments", "p-value"])) NULL else summary_iv$diagnostics["Weak instruments", "p-value"]
            if (is.null(wi_stat) && is.null(wi_p)) NULL else list(statistic = wi_stat, p_value = wi_p)
        },
        wu_hausman = {
            wh_stat <- if (is.na(summary_iv$diagnostics["Wu-Hausman", "statistic"])) NULL else summary_iv$diagnostics["Wu-Hausman", "statistic"]
            wh_p <- if (is.na(summary_iv$diagnostics["Wu-Hausman", "p-value"])) NULL else summary_iv$diagnostics["Wu-Hausman", "p-value"]
            if (is.null(wh_stat) && is.null(wh_p)) NULL else list(statistic = wh_stat, p_value = wh_p)
        },
        sargan = {
            s_stat <- if (is.na(summary_iv$diagnostics["Sargan", "statistic"])) NULL else summary_iv$diagnostics["Sargan", "statistic"]
            s_p <- if (is.na(summary_iv$diagnostics["Sargan", "p-value"])) NULL else summary_iv$diagnostics["Sargan", "p-value"]
            if (is.null(s_stat) && is.null(s_p)) NULL else list(statistic = s_stat, p_value = s_p)
        },
        robust_se = robust,
        formula = formula_str,
        n_obs = nobs(iv_model)
    )
    """
    try:
        result = await execute_r_script_async(r_script, params)
        await context.info("Instrumental variables model fitted successfully")
        return result
    except Exception as e:
        await context.error("Instrumental variables fitting failed", error=str(e))
        raise


@tool(
    name="var_model",
    input_schema={
        "type": "object",
        "properties": {
            "data": table_schema(),
            "variables": {"type": "array", "items": {"type": "string"}},
            "lags": {"type": "integer", "minimum": 1, "maximum": 10, "default": 2},
            "type": {
                "type": "string",
                "enum": ["const", "trend", "both", "none"],
                "default": "const",
            },
        },
        "required": ["data", "variables"],
    },
    output_schema={
        "type": "object",
        "properties": {
            "equations": {
                "type": "object",
                "description": "Results for each equation in the VAR system",
                "additionalProperties": {
                    "type": "object",
                    "properties": {
                        "coefficients": {
                            "type": "object",
                            "additionalProperties": {"type": "number"},
                            "description": "Coefficient estimates",
                        },
                        "std_errors": {
                            "type": "object",
                            "additionalProperties": {"type": "number"},
                            "description": "Standard errors",
                        },
                        "t_values": {
                            "type": "object",
                            "additionalProperties": {"type": "number"},
                            "description": "t-statistics",
                        },
                        "p_values": {
                            "type": "object",
                            "additionalProperties": {"type": "number"},
                            "description": "P-values",
                        },
                        "r_squared": {
                            "type": "number",
                            "minimum": 0,
                            "maximum": 1,
                            "description": "R-squared for this equation",
                        },
                        "adj_r_squared": {
                            "type": "number",
                            "maximum": 1,
                            "description": "Adjusted R-squared for this equation",
                        },
                    },
                },
            },
            "variables": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Variables included in the VAR system",
            },
            "lag_order": {
                "type": "integer",
                "description": "Number of lags in the VAR model",
                "minimum": 1,
                "maximum": 10,
            },
            "var_type": {
                "type": "string",
                "enum": ["const", "trend", "both", "none"],
                "description": "Type of deterministic terms included",
            },
            "n_obs": {
                "type": "integer",
                "description": "Number of observations used",
                "minimum": 1,
            },
            "n_variables": {
                "type": "integer",
                "description": "Number of variables in the system",
                "minimum": 2,
            },
            "loglik": {"type": "number", "description": "Log-likelihood value"},
            "aic": {"type": "number", "description": "Akaike Information Criterion"},
            "bic": {"type": "number", "description": "Bayesian Information Criterion"},
            "residual_covariance": {
                "type": "array",
                "items": {"type": "array", "items": {"type": "number"}},
                "description": "Residual covariance matrix",
            },
        },
        "required": [
            "equations",
            "variables",
            "lag_order",
            "var_type",
            "n_obs",
            "n_variables",
            "loglik",
            "aic",
            "bic",
            "residual_covariance",
        ],
        "additionalProperties": False,
    },
    description="Vector Autoregression (VAR) model for multivariate time series",
)
async def var_model(context, params) -> dict[str, Any]:
    """Fit Vector Autoregression model."""
    await context.info("Fitting VAR model")
    r_script = """
    library(vars)
    data <- as.data.frame(args$data)
    variables <- args$variables
    lag_order <- args$lags %||% 2
    var_type <- args$type %||% "const"
    # Select variables for VAR
    var_data <- data[, variables, drop = FALSE]
    # Remove missing values
    var_data <- na.omit(var_data)
    # Fit VAR model
    var_model <- VAR(var_data, p = lag_order, type = var_type)
    # Extract coefficients for each equation
    equations <- list()
    for (var in variables) {
        eq_summary <- summary(var_model)$varresult[[var]]
        equations[[var]] <- list(
            coefficients = as.list(coef(eq_summary)),
            std_errors = as.list(eq_summary$coefficients[, "Std. Error"]),
            t_values = as.list(eq_summary$coefficients[, "t value"]),
            p_values = as.list(eq_summary$coefficients[, "Pr(>|t|)"]),
            r_squared = eq_summary$r.squared,
            adj_r_squared = eq_summary$adj.r.squared
        )
    }
    # Model diagnostics
    var_summary <- summary(var_model)
    result <- list(
        equations = equations,
        variables = variables,
        lag_order = lag_order,
        var_type = var_type,
        n_obs = nobs(var_model),
        n_variables = length(variables),
        loglik = logLik(var_model)[1],
        aic = AIC(var_model),
        bic = BIC(var_model),
        residual_covariance = as.matrix(var_summary$covres)
    )
    """
    try:
        result = await execute_r_script_async(r_script, params)
        await context.info("VAR model fitted successfully")
        return result
    except Exception as e:
        await context.error("VAR model fitting failed", error=str(e))
        raise
