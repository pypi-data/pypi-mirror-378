"""管理员视图模块"""

from flask import Blueprint, request, jsonify, render_template

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/orders')
def list_orders():
    """
    列出所有订单
    
    Returns:
        订单列表页面
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # 获取订单列表
    orders = get_orders_paginated(page, per_page)
    
    return render_template('admin/orders.html', orders=orders)


@admin_bp.route('/orders/<order_id>/status', methods=['POST'])
def change_order_status(order_id):
    """
    修改订单状态
    
    Args:
        order_id: 订单ID
        
    Returns:
        操作结果
    """
    new_status = request.json.get('status')
    
    if new_status not in ['pending', 'paid', 'shipped', 'delivered', 'cancelled']:
        return jsonify({'error': '无效的状态'}), 400
    
    # 更新订单状态
    update_order_status(order_id, new_status)
    
    return jsonify({'success': True, 'message': '状态更新成功'})


@admin_bp.route('/payments/<payment_id>/refund', methods=['POST'])
def change_status_to_refund(payment_id):
    """
    将支付状态改为退款
    
    Args:
        payment_id: 支付ID
        
    Returns:
        操作结果
    """
    refund_amount = request.json.get('amount')
    reason = request.json.get('reason', '')
    
    # 处理退款
    result = process_refund(payment_id, refund_amount, reason)
    
    if result['success']:
        return jsonify({'success': True, 'message': '退款处理成功'})
    else:
        return jsonify({'error': result['error']}), 400


def get_orders_paginated(page, per_page):
    """
    分页获取订单
    
    Args:
        page: 页码
        per_page: 每页数量
        
    Returns:
        订单列表
    """
    # 模拟数据库查询
    return []


def update_order_status(order_id, status):
    """
    更新订单状态
    
    Args:
        order_id: 订单ID
        status: 新状态
    """
    print(f"更新订单 {order_id} 状态为 {status}")


def process_refund(payment_id, amount, reason):
    """
    处理退款
    
    Args:
        payment_id: 支付ID
        amount: 退款金额
        reason: 退款原因
        
    Returns:
        处理结果
    """
    print(f"处理退款: {payment_id}, 金额: {amount}, 原因: {reason}")
    return {'success': True}