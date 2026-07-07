"""
Email service for sending notifications
"""

import aiosmtplib
from email.message import EmailMessage
from typing import List, Optional
from datetime import datetime
import logging

from backend.config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class EmailService:
    """Service for sending email notifications"""
    
    def __init__(self):
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_username = settings.smtp_username
        self.smtp_password = settings.smtp_password
        self.smtp_from_email = settings.smtp_from_email
        self.smtp_use_tls = settings.smtp_use_tls
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """
        Send an email
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML content of the email
            text_content: Plain text content (optional)
        
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        if not self.smtp_username or not self.smtp_password:
            logger.warning("SMTP credentials not configured, skipping email")
            return False
        
        try:
            message = EmailMessage()
            message["From"] = self.smtp_from_email
            message["To"] = to_email
            message["Subject"] = subject
            
            message.set_content(text_content or html_content)
            message.add_alternative(html_content, subtype="html")
            
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_username,
                password=self.smtp_password,
                use_tls=self.smtp_use_tls
            )
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
    
    async def send_news_digest(
        self,
        to_email: str,
        user_name: str,
        articles: List[dict],
        categories: List[str]
    ) -> bool:
        """
        Send news digest email to user
        
        Args:
            to_email: Recipient email address
            user_name: User's name
            articles: List of articles to include in digest
            categories: User's subscribed categories
        
        Returns:
            bool: True if email sent successfully
        """
        # Generate HTML content
        html_content = self._generate_digest_html(user_name, articles, categories)
        text_content = self._generate_digest_text(user_name, articles, categories)
        
        subject = f"Your AI News Digest - {datetime.now().strftime('%B %d, %Y')}"
        
        return await self.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )
    
    def _generate_digest_html(
        self,
        user_name: str,
        articles: List[dict],
        categories: List[str]
    ) -> str:
        """Generate HTML content for news digest"""
        articles_html = ""
        
        for article in articles[:10]:  # Limit to 10 articles
            articles_html += f"""
            <div style="margin-bottom: 30px; padding-bottom: 20px; border-bottom: 1px solid #e0e0e0;">
                <h3 style="margin: 0 0 10px 0; color: #333;">
                    <a href="{article.get('url', '#')}" style="color: #0066cc; text-decoration: none;">
                        {article.get('title', 'No title')}
                    </a>
                </h3>
                <p style="margin: 5px 0; color: #666; font-size: 14px;">
                    <strong>Source:</strong> {article.get('source', 'Unknown')} | 
                    <strong>Category:</strong> {article.get('category', 'General')} | 
                    <strong>Published:</strong> {article.get('published_at', 'Unknown')}
                </p>
                <p style="margin: 10px 0; color: #444; line-height: 1.6;">
                    {article.get('description', article.get('content', ''))[:300]}...
                </p>
            </div>
            """
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Your AI News Digest</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 20px; background-color: #f4f4f4;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <div style="text-align: center; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 2px solid #0066cc;">
                    <h1 style="margin: 0; color: #0066cc;">AI News Digest</h1>
                    <p style="margin: 5px 0; color: #666;">Your personalized news summary</p>
                </div>
                
                <p style="margin: 0 0 20px 0; color: #666;">
                    Hello <strong>{user_name}</strong>,
                </p>
                <p style="margin: 0 0 30px 0; color: #444;">
                    Here's your daily news digest based on your interests in: 
                    <strong>{', '.join(categories)}</strong>
                </p>
                
                {articles_html}
                
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e0e0e0; text-align: center;">
                    <p style="margin: 0; color: #666; font-size: 12px;">
                        You're receiving this because you subscribed to AI News App notifications.
                    </p>
                    <p style="margin: 10px 0 0 0; color: #666; font-size: 12px;">
                        <a href="#" style="color: #0066cc;">Unsubscribe</a> | 
                        <a href="#" style="color: #0066cc;">Manage Preferences</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _generate_digest_text(
        self,
        user_name: str,
        articles: List[dict],
        categories: List[str]
    ) -> str:
        """Generate plain text content for news digest"""
        text = f"AI News Digest - {datetime.now().strftime('%B %d, %Y')}\n\n"
        text += f"Hello {user_name},\n\n"
        text += f"Here's your daily news digest based on your interests in: {', '.join(categories)}\n\n"
        text += "=" * 60 + "\n\n"
        
        for article in articles[:10]:
            text += f"TITLE: {article.get('title', 'No title')}\n"
            text += f"Source: {article.get('source', 'Unknown')} | "
            text += f"Category: {article.get('category', 'General')}\n"
            text += f"URL: {article.get('url', '#')}\n"
            text += f"{article.get('description', article.get('content', ''))[:200]}...\n\n"
            text += "-" * 60 + "\n\n"
        
        text += "\nYou're receiving this because you subscribed to AI News App notifications.\n"
        
        return text


# Global email service instance
email_service = EmailService()
