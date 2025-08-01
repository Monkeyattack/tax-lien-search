import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
from decouple import config
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.api_key = config('SENDGRID_API_KEY', default='')
        self.from_email = config('FROM_EMAIL', default='noreply@monkeyattack.com')
        self.from_name = config('FROM_NAME', default='Tax Lien Tracker')
        
        if self.api_key:
            self.sg = sendgrid.SendGridAPIClient(api_key=self.api_key)
        else:
            self.sg = None
            logger.warning("SendGrid API key not configured")
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        plain_text_content: str = None
    ) -> bool:
        """Send an email using SendGrid"""
        
        if not self.sg:
            logger.error("SendGrid not configured")
            return False
        
        try:
            from_email = Email(self.from_email, self.from_name)
            to_email = To(to_email)
            
            # Use HTML content as plain text if not provided
            if not plain_text_content:
                plain_text_content = html_content
            
            content = Content("text/html", html_content)
            mail = Mail(from_email, to_email, subject, content)
            
            # Add plain text version
            mail.add_content(Content("text/plain", plain_text_content))
            
            response = self.sg.client.mail.send.post(request_body=mail.get())
            
            if response.status_code == 202:
                logger.info(f"Email sent successfully to {to_email}")
                return True
            else:
                logger.error(f"Failed to send email. Status code: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False
    
    def send_redemption_deadline_alert(
        self,
        user_email: str,
        user_name: str,
        property_address: str,
        redemption_deadline: str,
        days_remaining: int,
        investment_amount: float
    ) -> bool:
        """Send redemption deadline alert email"""
        
        subject = f"Redemption Deadline Alert - {days_remaining} days remaining"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #d32f2f;">Tax Lien Redemption Alert</h2>
                
                <p>Dear {user_name},</p>
                
                <p>This is an important reminder about your tax lien investment:</p>
                
                <div style="background-color: #fff3cd; border: 1px solid #ffc107; border-radius: 5px; padding: 15px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #856404;">Property Information</h3>
                    <p><strong>Address:</strong> {property_address}</p>
                    <p><strong>Investment Amount:</strong> ${investment_amount:,.2f}</p>
                    <p><strong>Redemption Deadline:</strong> {redemption_deadline}</p>
                    <p><strong>Days Remaining:</strong> {days_remaining} days</p>
                </div>
                
                <div style="background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 5px; padding: 15px; margin: 20px 0;">
                    <h3 style="margin-top: 0;">What This Means</h3>
                    <p>If the property owner redeems within the redemption period, you will receive your investment back plus a 25% penalty (or 50% for second-year redemptions on homestead properties).</p>
                    
                    <p>If the redemption period expires without redemption, you will gain clear title to the property.</p>
                </div>
                
                <div style="background-color: #d1ecf1; border: 1px solid #b8daff; border-radius: 5px; padding: 15px; margin: 20px 0;">
                    <h3 style="margin-top: 0;">Action Items</h3>
                    <ul>
                        <li>Monitor the property for any redemption activity</li>
                        <li>Ensure your contact information is up to date with the county</li>
                        <li>Prepare for either redemption payment or title clearing process</li>
                        <li>Consider obtaining title insurance after redemption period expires</li>
                    </ul>
                </div>
                
                <p>Log in to your Tax Lien Tracker account to view more details and manage your investments.</p>
                
                <p>Best regards,<br>
                Tax Lien Tracker Team</p>
                
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
                <p style="font-size: 12px; color: #666;">
                    This is an automated alert. Please do not reply to this email.
                </p>
            </div>
        </body>
        </html>
        """
        
        plain_text = f"""
        Tax Lien Redemption Alert
        
        Dear {user_name},
        
        This is an important reminder about your tax lien investment:
        
        Property Address: {property_address}
        Investment Amount: ${investment_amount:,.2f}
        Redemption Deadline: {redemption_deadline}
        Days Remaining: {days_remaining} days
        
        If the property owner redeems within the redemption period, you will receive your investment back plus a 25% penalty (or 50% for second-year redemptions on homestead properties).
        
        If the redemption period expires without redemption, you will gain clear title to the property.
        
        Action Items:
        - Monitor the property for any redemption activity
        - Ensure your contact information is up to date with the county
        - Prepare for either redemption payment or title clearing process
        - Consider obtaining title insurance after redemption period expires
        
        Log in to your Tax Lien Tracker account to view more details and manage your investments.
        
        Best regards,
        Tax Lien Tracker Team
        """
        
        return self.send_email(user_email, subject, html_content, plain_text)
    
    def send_investment_summary(
        self,
        user_email: str,
        user_name: str,
        total_invested: float,
        active_investments: int,
        total_profit: float,
        avg_return: float
    ) -> bool:
        """Send investment portfolio summary email"""
        
        subject = "Your Tax Lien Investment Summary"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2e7d32;">Investment Portfolio Summary</h2>
                
                <p>Dear {user_name},</p>
                
                <p>Here's a summary of your tax lien investment portfolio:</p>
                
                <div style="background-color: #e8f5e8; border: 1px solid #4caf50; border-radius: 5px; padding: 20px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #2e7d32;">Portfolio Overview</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Total Invested:</strong></td>
                            <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align: right;">${total_invested:,.2f}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Active Investments:</strong></td>
                            <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align: right;">{active_investments}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Total Profit:</strong></td>
                            <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align: right;">${total_profit:,.2f}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px;"><strong>Average Return:</strong></td>
                            <td style="padding: 10px; text-align: right;">{avg_return:.1f}%</td>
                        </tr>
                    </table>
                </div>
                
                <p>Log in to your Tax Lien Tracker account for detailed information about each investment.</p>
                
                <p>Best regards,<br>
                Tax Lien Tracker Team</p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(user_email, subject, html_content)

# Global email service instance
email_service = EmailService()