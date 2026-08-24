from __future__ import annotations

import sqlite3
from datetime import date

import pandas as pd
import streamlit as st

from database.db import init_db, execute
from services.product_service import create_product, list_products
from services.purchase_order_service import (
    create_purchase_order,
    list_purchase_orders,
)
from services.risk_service import (
    dashboard_metrics,
    calculate_risk,
    save_risk_assessment,
    supplier_history,
    latest_risk_register,
    FACTOR_LABELS,
)
from services.supplier_service import create_supplier, list_suppliers
from services.weather_service import (
    get_live_weather,
    save_weather_assessment,
    latest_weather_for_supplier,
    weather_risk_register,
)
from services.simulation_service import calculate_simulation
from ml.predict import predict_disruption
from nlp.news_analyzer import analyze_news


st.set_page_config(
    page_title="SupplyChain Sentinel AI",
    page_icon="🛡️",
    layout="wide",
)


THEME_CSS = """
<style>
.block-container {padding-top: 1.5rem;}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
}
[data-testid="stSidebar"] * {
    color: #f8fafc;
}
.hero {
    padding: 1.4rem;
    border-radius: 18px;
    background: linear-gradient(135deg, #0f766e, #1d4ed8);
    color: white;
    margin-bottom: 1rem;
}
.hero h1 {
    margin: 0;
    font-size: 2rem;
}
.hero p {
    margin: .35rem 0 0;
    opacity: .9;
}
.metric-card {
    padding: 1rem;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    background: #ffffff;
    box-shadow: 0 8px 24px rgba(15, 23, 42, .06);
}
.section-card {
    padding: 1.2rem;
    border-radius: 16px;
    border: 1px solid #e2e8f0;
    background: #f8fafc;
    margin: .75rem 0;
}
.badge {
    display:inline-block;
    padding:.25rem .6rem;
    border-radius:999px;
    background:#dbeafe;
    color:#1e40af;
    font-weight:600;
}
</style>
"""

st.markdown(THEME_CSS, unsafe_allow_html=True)

init_db()


def hero(title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class='hero'>
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def dataframe(rows: list[dict], empty_message: str) -> None:
    if rows:
        st.dataframe(
            pd.DataFrame(rows),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info(empty_message)


def dashboard_page() -> None:

    metrics = dashboard_metrics()

    health = metrics.get("health", 0)
    total_suppliers = metrics.get("total_suppliers", 0)
    high_risk = metrics.get("high_risk_suppliers", 0)
    active_pos = metrics.get("active_purchase_orders", 0)
    assessed = metrics.get("total_assessed", 0)
    distribution = metrics.get("distribution", {})
    recent_alerts = metrics.get("recent_alerts", [])

    # ==============================
    # HERO SECTION
    # ==============================

    hero(
        "SupplyChain Sentinel AI",
        "AI-powered supply chain risk & disruption intelligence command center.",
    )

    st.caption(
        "Monitor suppliers, products, purchase orders, operational risks, "
        "weather disruptions, ML predictions, and news intelligence from one platform."
    )

    # ==============================
    # KPI SECTION
    # ==============================

    st.markdown("## Supply Chain Overview")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            "Supply Chain Health",
            f"{health}%",
        )
        st.progress(
            min(max(health / 100, 0), 1)
        )

    with col2:
        st.metric(
            "Total Suppliers",
            total_suppliers,
        )

    with col3:
        st.metric(
            "High Risk Suppliers",
            high_risk,
        )

    with col4:
        st.metric(
            "Active Purchase Orders",
            active_pos,
        )

    with col5:
        st.metric(
            "Suppliers Assessed",
            assessed,
        )

    st.divider()

    # ==============================
    # SMART ALERT & DECISION CENTER
    # ==============================

    st.markdown("## 🚨 Smart Alert & Decision Center")

    smart_alerts = []

    # ------------------------------
    # LOW INVENTORY ALERTS
    # ------------------------------

    products = list_products()

    low_inventory_products = [
        product
        for product in products
        if product.get("inventory_level", 0) <= 20
    ]

    for product in low_inventory_products:

        smart_alerts.append(
            {
                "Priority": "High",
                "Alert Type": "Low Inventory",
                "Item": product.get(
                    "name",
                    "Unknown Product",
                ),
                "Details": (
                    f"Inventory is only "
                    f"{product.get('inventory_level', 0)} units."
                ),
                "Recommended Action": (
                    "Review demand and create or expedite "
                    "a purchase order."
                ),
            }
        )

    # ------------------------------
    # DELAYED PURCHASE ORDER ALERTS
    # ------------------------------

    purchase_orders = list_purchase_orders()

    delayed_pos = [
        po
        for po in purchase_orders
        if po.get("status") == "Delayed"
    ]

    for po in delayed_pos:

        smart_alerts.append(
            {
                "Priority": "Critical",
                "Alert Type": "Delayed Purchase Order",
                "Item": po.get(
                    "po_number",
                    "Unknown PO",
                ),
                "Details": (
                    "Purchase order is currently marked "
                    "as delayed."
                ),
                "Recommended Action": (
                    "Contact the supplier, review delivery "
                    "status, and consider alternative sourcing."
                ),
            }
        )

    # ------------------------------
    # HIGH / CRITICAL RISK ALERTS
    # ------------------------------

    for alert in recent_alerts:

        risk_level = str(
            alert.get(
                "risk_level",
                "",
            )
        )

        if risk_level in ["High", "Critical"]:

            priority = (
                "Critical"
                if risk_level == "Critical"
                else "High"
            )

            smart_alerts.append(
                {
                    "Priority": priority,
                    "Alert Type": "Supplier Risk",
                    "Item": (
                        f"Supplier ID "
                        f"{alert.get('supplier_id', '-')}"
                    ),
                    "Details": (
                        f"Risk score: "
                        f"{alert.get('risk_score', 0)} "
                        f"({risk_level})"
                    ),
                    "Recommended Action": (
                        "Review supplier performance, "
                        "evaluate alternatives, and increase "
                        "safety stock if required."
                    ),
                }
            )

    # ------------------------------
    # DISPLAY SMART ALERTS
    # ------------------------------

    if smart_alerts:

        critical_count = sum(
            1
            for alert in smart_alerts
            if alert["Priority"] == "Critical"
        )

        high_count = sum(
            1
            for alert in smart_alerts
            if alert["Priority"] == "High"
        )

        alert_col1, alert_col2, alert_col3 = st.columns(3)

        with alert_col1:

            st.metric(
                "Total Active Alerts",
                len(smart_alerts),
            )

        with alert_col2:

            st.metric(
                "Critical Alerts",
                critical_count,
            )

        with alert_col3:

            st.metric(
                "High Priority Alerts",
                high_count,
            )

        st.dataframe(
            pd.DataFrame(smart_alerts),
            width="stretch",
            hide_index=True,
        )

        # Overall recommendation

        if critical_count > 0:

            st.error(
                "⚠️ Immediate attention required: Critical supply chain "
                "disruptions have been detected. Review delayed orders "
                "and critical supplier risks immediately."
            )

        elif high_count > 0:

            st.warning(
                "⚠️ High-priority operational risks detected. Review "
                "inventory levels, supplier risks, and purchase orders."
            )

    else:

        st.success(
            "✅ No major operational alerts detected. "
            "Current supply chain conditions appear stable."
        )

    st.divider()

    # ==============================
    # RISK + PLATFORM STATUS
    # ==============================

    left, right = st.columns([3, 2])

    with left:

        st.markdown("## 📊 Supplier Risk Distribution")

        risk_col1, risk_col2, risk_col3, risk_col4 = st.columns(4)

        with risk_col1:

            st.metric(
                "🟢 Low",
                distribution.get("Low", 0),
            )

        with risk_col2:

            st.metric(
                "🟡 Medium",
                distribution.get("Medium", 0),
            )

        with risk_col3:

            st.metric(
                "🟠 High",
                distribution.get("High", 0),
            )

        with risk_col4:

            st.metric(
                "🔴 Critical",
                distribution.get("Critical", 0),
            )

        chart_data = pd.DataFrame(
            {
                "Risk Level": [
                    "Low",
                    "Medium",
                    "High",
                    "Critical",
                ],
                "Suppliers": [
                    distribution.get("Low", 0),
                    distribution.get("Medium", 0),
                    distribution.get("High", 0),
                    distribution.get("Critical", 0),
                ],
            }
        )

        st.bar_chart(
            chart_data.set_index("Risk Level")
        )

    with right:

        st.markdown("## ⚡ System Status")

        st.success(
            "🤖 ML Disruption Prediction\n\n"
            "AI model available"
        )

        st.info(
            "🌦️ Weather Intelligence\n\n"
            "Supplier weather monitoring available"
        )

        st.warning(
            "📰 NLP News Intelligence\n\n"
            "Supply chain risk signal detection"
        )

        st.success(
            "🔬 What-If Simulation\n\n"
            "Scenario impact analysis ready"
        )

    st.divider()

    # ==============================
    # RECENT RISK ALERTS
    # ==============================

    st.markdown("## 📋 Recent Supplier Risk Assessments")

    if recent_alerts:

        alert_rows = []

        for alert in recent_alerts:

            alert_rows.append(
                {
                    "Risk Level": alert.get(
                        "risk_level",
                        "Unknown",
                    ),
                    "Risk Score": alert.get(
                        "risk_score",
                        0,
                    ),
                    "Supplier ID": alert.get(
                        "supplier_id",
                        "-",
                    ),
                    "Created At": alert.get(
                        "created_at",
                        "-",
                    ),
                }
            )

        st.dataframe(
            pd.DataFrame(alert_rows),
            width="stretch",
            hide_index=True,
        )

    else:

        st.info(
            "No supplier risk assessments have been recorded yet."
        )

    st.divider()

    # ==============================
    # AI INTELLIGENCE CENTER
    # ==============================

    st.markdown("## 🧠 AI Intelligence Center")

    ai1, ai2, ai3 = st.columns(3)

    with ai1:

        st.markdown(
            """
            ### 🤖 ML Prediction

            Predict the probability of a supply chain
            disruption using supplier, financial,
            delivery, inventory and weather risk factors.
            """
        )

    with ai2:

        st.markdown(
            """
            ### 🌦️ Weather Intelligence

            Monitor supplier locations and identify
            possible logistics and operational
            disruptions caused by weather conditions.
            """
        )

    with ai3:

        st.markdown(
            """
            ### 📰 NLP Risk Analysis

            Analyze news headlines and supply chain
            reports to identify disruption signals
            and potential operational risks.
            """
        )

    st.divider()

    # ==============================
    # RECOMMENDED WORKFLOW
    # ==============================

    st.markdown("## 🔄 Recommended Workflow")

    step1, step2, step3, step4 = st.columns(4)

    with step1:

        st.info(
            """
            **1. Manage Data**

            Add suppliers, products and
            purchase orders.
            """
        )

    with step2:

        st.warning(
            """
            **2. Assess Risk**

            Calculate supplier and
            operational risk.
            """
        )

    with step3:

        st.success(
            """
            **3. Use AI Intelligence**

            Analyze weather, ML
            predictions and news risks.
            """
        )

    with step4:

        st.info(
            """
            **4. Plan Response**

            Run What-If simulations
            and apply mitigation actions.
            """
        )


def suppliers_page() -> None:

    hero(
        "Supplier Management",
        "Maintain supplier master data with durable SQLite persistence.",
    )

    # ==============================
    # ADD SUPPLIER
    # ==============================

    with st.form(
        "supplier_form",
        clear_on_submit=True,
    ):

        c1, c2 = st.columns(2)

        name = c1.text_input(
            "Supplier Name"
        )

        location = c2.text_input(
            "Location / City"
        )

        country = c1.text_input(
            "Country"
        )

        product_category = c2.text_input(
            "Product Category"
        )

        contact = c1.text_input(
            "Contact Information"
        )

        status = c2.selectbox(
            "Status",
            ["Active", "Watchlist", "Inactive"],
        )

        submitted = st.form_submit_button(
            "Add Supplier",
            type="primary",
        )

        if submitted:

            if not all(
                [
                    name,
                    location,
                    country,
                    product_category,
                    contact,
                ]
            ):

                st.error(
                    "Please complete all supplier fields."
                )

            else:

                create_supplier(
                    name,
                    location,
                    country,
                    product_category,
                    contact,
                    status,
                )

                st.success(
                    "Supplier added successfully."
                )

                st.rerun()

    # ==============================
    # SUPPLIER RECORDS
    # ==============================

    suppliers = list_suppliers()

    dataframe(
        suppliers,
        "No suppliers have been added yet.",
    )

    # ==============================
    # MANAGE / DELETE SUPPLIER
    # ==============================

    if suppliers:

        st.divider()

        st.subheader(
            "🗑️ Manage Supplier Data"
        )

        st.caption(
            "Select a supplier to remove. "
            "Related products, purchase orders, risk assessments, "
            "and weather assessments will also be deleted."
        )

        supplier_options = {
            f"ID {s['id']} — {s['name']} ({s['country']})": s["id"]
            for s in suppliers
        }

        selected_supplier = st.selectbox(
            "Select supplier",
            list(supplier_options.keys()),
            key="delete_supplier_select",
        )

        selected_supplier_id = (
            supplier_options[selected_supplier]
        )

        # First step:
        # Ask for deletion confirmation

        if not st.session_state.get(
            "confirm_supplier_delete",
            False,
        ):

            if st.button(
                "🗑️ Delete Supplier",
                key="delete_supplier_button",
            ):

                st.session_state[
                    "confirm_supplier_delete"
                ] = True

                st.session_state[
                    "supplier_to_delete"
                ] = selected_supplier_id

                st.rerun()

        # Second step:
        # Show confirmation

        else:

            st.warning(
                "⚠️ Are you sure you want to delete this supplier?"
            )

            st.caption(
                "This will permanently delete the supplier and all "
                "related products, purchase orders, risk assessments, "
                "and weather assessments."
            )

            confirm_col, cancel_col = st.columns(2)

            with confirm_col:

                if st.button(
                    "Yes, Delete Permanently",
                    type="primary",
                    key="confirm_supplier_delete_button",
                ):

                    supplier_id = st.session_state.get(
                        "supplier_to_delete"
                    )

                    try:

                        # Delete related purchase orders
                        execute(
                            """
                            DELETE FROM purchase_orders
                            WHERE supplier_id = ?
                            """,
                            (supplier_id,),
                        )

                        # Delete purchase orders linked
                        # through supplier products

                        execute(
                            """
                            DELETE FROM purchase_orders
                            WHERE product_id IN (
                                SELECT id
                                FROM products
                                WHERE supplier_id = ?
                            )
                            """,
                            (supplier_id,),
                        )

                        # Delete products

                        execute(
                            """
                            DELETE FROM products
                            WHERE supplier_id = ?
                            """,
                            (supplier_id,),
                        )

                        # Delete risk assessments

                        execute(
                            """
                            DELETE FROM risk_assessments
                            WHERE supplier_id = ?
                            """,
                            (supplier_id,),
                        )

                        # Delete weather assessments

                        execute(
                            """
                            DELETE FROM weather_assessments
                            WHERE supplier_id = ?
                            """,
                            (supplier_id,),
                        )

                        # Finally delete supplier

                        execute(
                            """
                            DELETE FROM suppliers
                            WHERE id = ?
                            """,
                            (supplier_id,),
                        )

                        # Reset confirmation state

                        st.session_state[
                            "confirm_supplier_delete"
                        ] = False

                        st.session_state[
                            "supplier_to_delete"
                        ] = None

                        st.success(
                            "Supplier and all related data "
                            "deleted successfully."
                        )

                        st.rerun()

                    except sqlite3.Error as exc:

                        st.error(
                            f"Unable to delete supplier: {exc}"
                        )

            with cancel_col:

                if st.button(
                    "Cancel",
                    key="cancel_supplier_delete",
                ):

                    st.session_state[
                        "confirm_supplier_delete"
                    ] = False

                    st.session_state[
                        "supplier_to_delete"
                    ] = None

                    st.rerun()


def products_page() -> None:

    hero(
        "Product Management",
        "Connect products to suppliers and track operating inventory context.",
    )

    suppliers = list_suppliers()

    supplier_options = {
        f"{s['name']} ({s['country']})": s["id"]
        for s in suppliers
    }

    # ==============================
    # ADD PRODUCT
    # ==============================

    with st.form(
        "product_form",
        clear_on_submit=True,
    ):

        c1, c2 = st.columns(2)

        name = c1.text_input(
            "Product Name"
        )

        sku = c2.text_input(
            "SKU"
        )

        category = c1.text_input(
            "Category"
        )

        supplier_label = (
            c2.selectbox(
                "Supplier",
                list(supplier_options.keys()),
            )
            if supplier_options
            else None
        )

        unit_cost = c1.number_input(
            "Unit Cost",
            min_value=0.0,
            step=1.0,
        )

        inventory = c2.number_input(
            "Inventory Level",
            min_value=0,
            step=1,
        )

        status = c1.selectbox(
            "Status",
            ["Active", "Constrained", "Retired"],
        )

        submitted = st.form_submit_button(
            "Add Product",
            type="primary",
        )

        if submitted:

            if (
                not all([name, sku, category])
                or supplier_label is None
            ):

                st.error(
                    "Please complete product fields and add "
                    "at least one supplier first."
                )

            else:

                try:

                    create_product(
                        name,
                        sku,
                        category,
                        supplier_options[supplier_label],
                        unit_cost,
                        inventory,
                        status,
                    )

                    st.success(
                        "Product added successfully."
                    )

                    st.rerun()

                except sqlite3.IntegrityError:

                    st.error(
                        "SKU must be unique."
                    )

    # ==============================
    # PRODUCT RECORDS
    # ==============================

    products = list_products()

    dataframe(
        products,
        "No products have been added yet.",
    )

    # ==============================
    # MANAGE / DELETE PRODUCT
    # ==============================

    if products:

        st.divider()

        st.subheader(
            "🗑️ Manage Product Data"
        )

        st.caption(
            "Select a product to remove. "
            "Any purchase orders linked to this product "
            "will also be deleted."
        )

        product_options = {
            f"ID {p['id']} — {p['name']} ({p['sku']})": p["id"]
            for p in products
        }

        selected_product = st.selectbox(
            "Select product",
            list(product_options.keys()),
            key="delete_product_select",
        )

        selected_product_id = (
            product_options[selected_product]
        )

        # First step: request confirmation

        if not st.session_state.get(
            "confirm_product_delete",
            False,
        ):

            if st.button(
                "🗑️ Delete Product",
                key="delete_product_button",
            ):

                st.session_state[
                    "confirm_product_delete"
                ] = True

                st.session_state[
                    "product_to_delete"
                ] = selected_product_id

                st.rerun()

        # Second step: confirmation

        else:

            st.warning(
                "⚠️ Are you sure you want to delete this product?"
            )

            st.caption(
                "This will permanently delete the product and "
                "any purchase orders linked to it."
            )

            confirm_col, cancel_col = st.columns(2)

            with confirm_col:

                if st.button(
                    "Yes, Delete Permanently",
                    type="primary",
                    key="confirm_product_delete_button",
                ):

                    product_id = st.session_state.get(
                        "product_to_delete"
                    )

                    try:

                        # Delete linked purchase orders first

                        execute(
                            """
                            DELETE FROM purchase_orders
                            WHERE product_id = ?
                            """,
                            (product_id,),
                        )

                        # Delete the product

                        execute(
                            """
                            DELETE FROM products
                            WHERE id = ?
                            """,
                            (product_id,),
                        )

                        # Reset confirmation state

                        st.session_state[
                            "confirm_product_delete"
                        ] = False

                        st.session_state[
                            "product_to_delete"
                        ] = None

                        st.success(
                            "Product and related purchase orders "
                            "deleted successfully."
                        )

                        st.rerun()

                    except sqlite3.Error as exc:

                        st.error(
                            f"Unable to delete product: {exc}"
                        )

            with cancel_col:

                if st.button(
                    "Cancel",
                    key="cancel_product_delete",
                ):

                    st.session_state[
                        "confirm_product_delete"
                    ] = False

                    st.session_state[
                        "product_to_delete"
                    ] = None

                    st.rerun()


def purchase_orders_page() -> None:

    hero(
        "Purchase Order Management",
        "Track active supply commitments and delivery status.",
    )

    suppliers = {
        f"{s['name']} ({s['country']})": s["id"]
        for s in list_suppliers()
    }

    products = {
        f"{p['name']} ({p['sku']})": p["id"]
        for p in list_products()
    }

    # ==============================
    # CREATE PURCHASE ORDER
    # ==============================

    with st.form(
        "po_form",
        clear_on_submit=True,
    ):

        c1, c2 = st.columns(2)

        po_number = c1.text_input(
            "PO Number"
        )

        supplier_label = (
            c2.selectbox(
                "Supplier",
                list(suppliers.keys()),
            )
            if suppliers
            else None
        )

        product_label = (
            c1.selectbox(
                "Product",
                list(products.keys()),
            )
            if products
            else None
        )

        quantity = c2.number_input(
            "Quantity",
            min_value=1,
            step=1,
        )

        order_date = c1.date_input(
            "Order Date",
            value=date.today(),
        )

        expected_delivery = c2.date_input(
            "Expected Delivery",
            value=date.today(),
        )

        status = c1.selectbox(
            "Status",
            [
                "Open",
                "In Transit",
                "Delivered",
                "Delayed",
                "Cancelled",
            ],
        )

        total_value = c2.number_input(
            "Total Value",
            min_value=0.0,
            step=100.0,
        )

        submitted = st.form_submit_button(
            "Create Purchase Order",
            type="primary",
        )

        if submitted:

            if (
                not po_number
                or supplier_label is None
                or product_label is None
            ):

                st.error(
                    "Please complete PO fields and add "
                    "suppliers/products first."
                )

            else:

                try:

                    create_purchase_order(
                        po_number,
                        suppliers[supplier_label],
                        products[product_label],
                        quantity,
                        str(order_date),
                        str(expected_delivery),
                        status,
                        total_value,
                    )

                    st.success(
                        "Purchase order created successfully."
                    )

                    st.rerun()

                except sqlite3.IntegrityError:

                    st.error(
                        "PO number must be unique."
                    )

    # ==============================
    # PURCHASE ORDER RECORDS
    # ==============================

    purchase_orders = list_purchase_orders()

    dataframe(
        purchase_orders,
        "No purchase orders have been created yet.",
    )

    # ==============================
    # MANAGE / DELETE PURCHASE ORDER
    # ==============================

    if purchase_orders:

        st.divider()

        st.subheader(
            "🗑️ Manage Purchase Order Data"
        )

        st.caption(
            "Select a purchase order to remove permanently."
        )

        po_options = {
            f"ID {po['id']} — {po['po_number']}": po["id"]
            for po in purchase_orders
        }

        selected_po = st.selectbox(
            "Select purchase order",
            list(po_options.keys()),
            key="delete_po_select",
        )

        selected_po_id = po_options[selected_po]

        # First step: request confirmation

        if not st.session_state.get(
            "confirm_po_delete",
            False,
        ):

            if st.button(
                "🗑️ Delete Purchase Order",
                key="delete_po_button",
            ):

                st.session_state[
                    "confirm_po_delete"
                ] = True

                st.session_state[
                    "po_to_delete"
                ] = selected_po_id

                st.rerun()

        # Second step: confirmation

        else:

            st.warning(
                "⚠️ Are you sure you want to delete this purchase order?"
            )

            st.caption(
                "This action cannot be undone."
            )

            confirm_col, cancel_col = st.columns(2)

            with confirm_col:

                if st.button(
                    "Yes, Delete Permanently",
                    type="primary",
                    key="confirm_po_delete_button",
                ):

                    po_id = st.session_state.get(
                        "po_to_delete"
                    )

                    try:

                        execute(
                            """
                            DELETE FROM purchase_orders
                            WHERE id = ?
                            """,
                            (po_id,),
                        )

                        st.session_state[
                            "confirm_po_delete"
                        ] = False

                        st.session_state[
                            "po_to_delete"
                        ] = None

                        st.success(
                            "Purchase order deleted successfully."
                        )

                        st.rerun()

                    except sqlite3.Error as exc:

                        st.error(
                            f"Unable to delete purchase order: {exc}"
                        )

            with cancel_col:

                if st.button(
                    "Cancel",
                    key="cancel_po_delete",
                ):

                    st.session_state[
                        "confirm_po_delete"
                    ] = False

                    st.session_state[
                        "po_to_delete"
                    ] = None

                    st.rerun()


# =========================================
# RISK INTELLIGENCE
# =========================================

def risk_intelligence_page() -> None:

    hero(
        "Risk Intelligence",
        "Explainable supplier risk scoring with historical assessment tracking.",
    )

    suppliers = list_suppliers()

    if not suppliers:

        st.info(
            "Add at least one supplier before "
            "generating a risk assessment."
        )

        return

    options = {
        f"{s['name']} · {s['country']}": s
        for s in suppliers
    }

    selected_label = st.selectbox(
        "Select Supplier",
        list(options.keys()),
    )

    supplier = options[selected_label]

    st.markdown(
        "### Risk Factor Assessment"
    )

    st.caption(
        "0 = no risk, 100 = maximum risk. "
        "The weighted engine calculates the final score."
    )

    with st.form(
        "risk_assessment_form"
    ):

        c1, c2 = st.columns(2)

        # IMPORTANT:
        # These keys now exactly match risk_service.py

        factors = {

            "reliability": c1.slider(
                "Supplier Reliability Risk",
                0,
                100,
                30,
            ),

            "geographic_risk": c2.slider(
                "Geographic Concentration Risk",
                0,
                100,
                25,
            ),

            "financial_stability": c1.slider(
                "Financial Stability Risk",
                0,
                100,
                20,
            ),

            "delivery_performance": c2.slider(
                "Delivery Performance Risk",
                0,
                100,
                30,
            ),

            "inventory_dependency": c1.slider(
                "Inventory Dependency Risk",
                0,
                100,
                25,
            ),
        }

        submitted = st.form_submit_button(
            "Generate & Save Risk Assessment",
            type="primary",
        )

    if submitted:

        result = calculate_risk(factors)

        save_risk_assessment(
            supplier["id"],
            result,
        )

        st.success(
            "Risk assessment saved successfully."
        )

        a, b, c = st.columns(3)

        a.metric(
            "Overall Risk Score",
            f'{result["risk_score"]}/100',
        )

        b.metric(
            "Risk Level",
            result["risk_level"],
        )

        c.metric(
            "Top Mitigation",
            FACTOR_LABELS[
                max(
                    result["contributions"],
                    key=result["contributions"].get,
                )
            ],
        )

        st.markdown(
            f"**Explanation:** "
            f"{result['explanation']}"
        )

        # FIXED: recommendation instead of mitigation_action

        st.info(
            f"**Recommended action:** "
            f"{result['recommendation']}"
        )

        st.bar_chart(
            result["contributions"]
        )

    st.markdown(
        "### Assessment History"
    )

    dataframe(
        supplier_history(
            supplier["id"]
        ),
        "No previous assessments for this supplier.",
    )

    st.markdown(
        "### Latest Supplier Risk Register"
    )

    dataframe(
        latest_risk_register(),
        "No supplier risk assessments available yet.",
    )


def weather_intelligence_page() -> None:

    hero(
        "Weather Intelligence",
        "Monitor live weather conditions around supplier locations and identify potential logistics disruptions.",
    )

    suppliers = list_suppliers()

    if not suppliers:

        st.info(
            "Add at least one supplier with a valid city "
            "and country before checking live weather."
        )

        return

    options = {
        f"{s['name']} · {s['location']}, {s['country']}": s
        for s in suppliers
    }

    selected_label = st.selectbox(
        "Select Supplier Location",
        list(options.keys()),
        key="weather_supplier",
    )

    supplier = options[selected_label]

    st.markdown(
        "### Live Supplier Weather Check"
    )

    st.caption(
        "Weather is fetched in real time from the "
        "supplier's saved location."
    )

    if st.button(
        "Check Live Weather & Generate Risk",
        type="primary",
    ):

        with st.spinner(
            "Fetching live weather and calculating disruption risk..."
        ):

            try:

                weather = get_live_weather(
                    supplier["location"],
                    supplier["country"],
                )

                save_weather_assessment(
                    supplier["id"],
                    weather,
                )

                st.session_state[
                    "latest_weather_result"
                ] = weather

                st.success(
                    f"Live weather updated for "
                    f"{weather['resolved_name']}."
                )

            except Exception as exc:

                st.error(
                    f"Unable to retrieve live weather: {exc}"
                )

    weather = st.session_state.get(
        "latest_weather_result"
    )

    if weather and selected_label:

        st.markdown(
            "### Current Conditions"
        )

        a, b, c, d = st.columns(4)

        a.metric(
            "Temperature",
            f"{weather.get('temperature_2m', 0):.1f} °C",
        )

        b.metric(
            "Feels Like",
            f"{weather.get('apparent_temperature', 0):.1f} °C",
        )

        c.metric(
            "Precipitation",
            f"{weather.get('precipitation', 0):.1f} mm",
        )

        d.metric(
            "Wind Speed",
            f"{weather.get('wind_speed_10m', 0):.1f} km/h",
        )

        x, y, z = st.columns(3)

        x.metric(
            "Weather Condition",
            weather["weather_condition"],
        )

        y.metric(
            "Weather Risk Score",
            f"{weather['weather_risk_score']}/100",
        )

        z.metric(
            "Risk Level",
            weather["weather_risk_level"],
        )

        st.markdown(
            f"**Disruption Analysis:** "
            f"{weather['alert_message']}"
        )

    st.markdown(
        "### Last Saved Weather Assessment"
    )

    previous = latest_weather_for_supplier(
        supplier["id"]
    )

    if previous:

        st.dataframe(
            pd.DataFrame([previous]),
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info(
            "No weather assessment has been saved "
            "for this supplier yet."
        )

    st.markdown(
        "### Supplier Weather Risk Register"
    )

    dataframe(
        weather_risk_register(),
        "No supplier weather assessments available yet.",
    )


def placeholder_page(
    title: str,
    subtitle: str,
) -> None:

    hero(
        title,
        subtitle,
    )

    st.markdown(
        """
        <div class='section-card'>
            <h3>Roadmap Ready</h3>
            <p>
                This workspace is intentionally scaffolded
                for future expansion without introducing
                premature ML, NLP, external API, or
                prediction logic.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def what_if_simulation_page():

    st.title(
        "What-If Simulation"
    )

    st.caption(
        "Simulate potential supply chain disruptions and "
        "evaluate their operational and financial impact."
    )

    st.subheader(
        "Scenario Parameters"
    )

    col1, col2 = st.columns(2)

    with col1:

        delivery_delay = st.slider(
            "Supplier Delivery Delay (Days)",
            min_value=0,
            max_value=60,
            value=5,
        )

        cost_increase = st.slider(
            "Cost Increase (%)",
            min_value=0.0,
            max_value=50.0,
            value=5.0,
        )

        demand_increase = st.slider(
            "Demand Increase (%)",
            min_value=0.0,
            max_value=100.0,
            value=10.0,
        )

    with col2:

        inventory_level = st.slider(
            "Current Inventory Level (%)",
            min_value=0.0,
            max_value=100.0,
            value=70.0,
        )

        weather_severity = st.selectbox(
            "Weather Severity",
            [
                "Low",
                "Medium",
                "High",
                "Critical",
            ],
        )

    st.divider()

    if st.button(
        "Run Simulation",
        use_container_width=True,
    ):

        result = calculate_simulation(
            delivery_delay=delivery_delay,
            cost_increase=cost_increase,
            demand_increase=demand_increase,
            inventory_level=inventory_level,
            weather_severity=weather_severity,
        )

        st.subheader(
            "Simulation Results"
        )

        metric1, metric2, metric3 = st.columns(3)

        metric1.metric(
            "Overall Disruption Score",
            f"{result['overall_score']}/100",
        )

        metric2.metric(
            "Risk Level",
            result["risk_level"],
        )

        metric3.metric(
            "Estimated Financial Impact",
            f"₹ {result['financial_impact']:,.2f}",
        )

        st.subheader(
            "Impact Breakdown"
        )

        impact_data = {
            "Delivery Delay": result[
                "delivery_impact"
            ],
            "Cost Increase": result[
                "cost_impact"
            ],
            "Demand Increase": result[
                "demand_impact"
            ],
            "Inventory Risk": result[
                "inventory_impact"
            ],
            "Weather Impact": result[
                "weather_impact"
            ],
        }

        st.bar_chart(
            impact_data
        )

        st.subheader(
            "Recommended Actions"
        )

        for recommendation in result[
            "recommendations"
        ]:

            st.info(
                recommendation
            )


def ml_disruption_prediction_page():

    st.title(
        "ML Disruption Prediction"
    )

    st.caption(
        "Use the trained machine learning model to predict "
        "the probability of supply chain disruption."
    )

    st.subheader(
        "Supply Chain Risk Inputs"
    )

    col1, col2 = st.columns(2)

    with col1:

        supplier_reliability = st.slider(
            "Supplier Reliability Risk",
            0,
            100,
            30,
        )

        geographic_risk = st.slider(
            "Geographic Risk",
            0,
            100,
            25,
        )

        financial_stability = st.slider(
            "Financial Stability Risk",
            0,
            100,
            20,
        )

    with col2:

        delivery_performance = st.slider(
            "Delivery Performance Risk",
            0,
            100,
            30,
        )

        inventory_dependency = st.slider(
            "Inventory Dependency Risk",
            0,
            100,
            25,
        )

        weather_risk = st.slider(
            "Weather Risk",
            0,
            100,
            20,
        )

    st.divider()

    if st.button(
        "Predict Disruption Risk",
        use_container_width=True,
    ):

        result = predict_disruption(
            supplier_reliability=supplier_reliability,
            geographic_risk=geographic_risk,
            financial_stability=financial_stability,
            delivery_performance=delivery_performance,
            inventory_dependency=inventory_dependency,
            weather_risk=weather_risk,
        )

        st.subheader(
            "ML Prediction Result"
        )

        metric1, metric2, metric3 = st.columns(3)

        metric1.metric(
            "Disruption Probability",
            f"{result['disruption_probability']}%",
        )

        metric2.metric(
            "Prediction",
            result["prediction"],
        )

        metric3.metric(
            "Risk Level",
            result["risk_level"],
        )

        st.subheader(
            "Model Performance"
        )

        st.metric(
            "Model Accuracy",
            f"{result['model_accuracy']}%",
        )

        probability = (
            result["disruption_probability"]
            / 100
        )

        st.progress(
            probability
        )

        st.subheader(
            "Risk Assessment"
        )

        if result["risk_level"] == "Low":

            st.success(
                "Low disruption probability. "
                "Current supply chain conditions appear stable."
            )

        elif result["risk_level"] == "Medium":

            st.warning(
                "Moderate disruption probability. "
                "Continue monitoring key supply chain factors."
            )

        elif result["risk_level"] == "High":

            st.warning(
                "High disruption probability. "
                "Consider mitigation actions and alternative suppliers."
            )

        else:

            st.error(
                "Critical disruption probability. "
                "Immediate supply chain mitigation is recommended."
            )


def news_risk_intelligence_page():

    st.title(
        "NLP News Risk Intelligence"
    )

    st.caption(
        "Analyze news headlines or supply chain reports "
        "to identify potential disruption signals."
    )

    st.subheader(
        "News / Risk Text Analysis"
    )

    news_text = st.text_area(
        "Enter a news headline, article excerpt, or supply chain update",
        height=180,
        placeholder=(
            "Example: Heavy rain and flooding have caused "
            "road closures, shipping delays, and material "
            "shortages in the region."
        ),
    )

    if st.button(
        "Analyze Risk",
        use_container_width=True,
    ):

        if not news_text.strip():

            st.warning(
                "Please enter some news or supply chain text to analyze."
            )

        else:

            result = analyze_news(
                news_text
            )

            st.subheader(
                "NLP Risk Analysis Result"
            )

            col1, col2 = st.columns(2)

            with col1:

                st.metric(
                    "Risk Score",
                    f"{result['risk_score']}/100",
                )

            with col2:

                st.metric(
                    "Risk Level",
                    result["risk_level"],
                )

            st.subheader(
                "Analysis Summary"
            )

            st.info(
                result["summary"]
            )

            if result[
                "detected_risks"
            ]:

                st.subheader(
                    "Detected Risk Categories"
                )

                for risk in result[
                    "detected_risks"
                ]:

                    st.write(
                        f"**{risk['category']}**: "
                        f"{', '.join(risk['keywords'])}"
                    )

                st.subheader(
                    "Matched Risk Keywords"
                )

                st.write(
                    ", ".join(
                        result["matched_keywords"]
                    )
                )

            else:

                st.success(
                    "No major supply chain disruption "
                    "keywords were detected."
                )

def settings_page() -> None:

    hero(
        "Settings",
        "Configure platform preferences and operational defaults."
    )

    st.markdown("### Platform Configuration")

    col1, col2 = st.columns(2)

    with col1:
        default_country = st.text_input(
            "Default Country",
            value="India"
        )

        risk_threshold = st.slider(
            "High Risk Threshold",
            min_value=50,
            max_value=100,
            value=75
        )

    with col2:
        weather_monitoring = st.toggle(
            "Enable Weather Monitoring",
            value=True
        )

        ai_predictions = st.toggle(
            "Enable AI Disruption Prediction",
            value=True
        )

    st.markdown("---")

    st.markdown("### Notification Preferences")

    email_alerts = st.checkbox(
        "Enable Email Risk Alerts",
        value=True
    )

    critical_alerts = st.checkbox(
        "Notify for Critical Risks",
        value=True
    )

    if st.button("Save Settings", type="primary"):

        st.success("Settings saved successfully.")

        st.info(
            f"Default Country: {default_country} | "
            f"High Risk Threshold: {risk_threshold}"
        )

PAGES = {

    "Dashboard": dashboard_page,

    "Suppliers": suppliers_page,

    "Products": products_page,

    "Purchase Orders": purchase_orders_page,

    "Risk Intelligence": risk_intelligence_page,

    "Weather Intelligence": weather_intelligence_page,

    "What-If Simulation": what_if_simulation_page,

    "ML Disruption Prediction": ml_disruption_prediction_page,

    "NLP News Intelligence": news_risk_intelligence_page,

     "Settings": settings_page,
}


st.sidebar.title(
    "🛡️ Sentinel AI"
)

st.sidebar.caption(
    "Supply chain risk intelligence"
)

selected_page = st.sidebar.radio(
    "Navigation",
    list(PAGES.keys()),
)

PAGES[selected_page]()