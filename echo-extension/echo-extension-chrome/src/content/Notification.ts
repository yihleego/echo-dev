import Prism from 'prismjs';
import ShadowDOMComponent from './ShadowDOMComponent';

/**
 * {@link displayMessage} about the current clicked element, see {@link registerEvents} cb, {@param getTargetCallback}.
 *
 * @class Notification
 * @extends ShadowDOMComponent
 */
class Notification extends ShadowDOMComponent {
  private notificationElement!: HTMLElement;

  constructor(shadowRoot: ShadowRoot) {
    super(shadowRoot);
    this.bindMethods();
    this.notificationElement = this.shadowRoot.querySelector('.new-element')!;
  }

  protected bindMethods(): void {
    this.displayMessage = this.displayMessage.bind(this);
  }

  private displayMessage(message: string): void {
    const msgDiv = document.createElement('div');
    msgDiv.innerHTML = `<code class='tl-code language-markup' id='msgDiv'>${message}</code>`;
    this.notificationElement.innerHTML = '';
    this.notificationElement.appendChild(msgDiv);
    this.notificationElement.classList.remove('show');
    this.notificationElement.classList.add('show');

    const element = this.shadowRoot.querySelector('#msgDiv');
    if (element) {
      Prism.highlightElement(element);
    } else {
      console.error('Element not found');
    }

    setTimeout(() => {
      if (this.notificationElement.classList.contains('show')) {
        this.notificationElement.classList.remove('show');
      }
    }, 2000);
  }

  registerEvents(getTargetCallback: () => HTMLElement): void {
    document.addEventListener('click', () => {
      const target = getTargetCallback();
      const message = `已选中: ${target.id || target.tagName}`;
      this.displayMessage(message);
      var rect = target.getBoundingClientRect();
      console.log('元素在文档中的左上角 X 坐标:', rect.left + window.screenLeft);
      console.log('元素在文档中的左上角 Y 坐标:', rect.top + window.screenTop);
      console.log('元素的宽度:', rect.width);
      console.log('元素的高度:', rect.height);
      var offsetX = 0;
      var offsetY = 0;
      // @ts-ignore
      if (window.screen.availLeft > 0 || window.screen.availTop > 0) {
        // @ts-ignore
        offsetX = window.screen.availLeft + window.screenLeft + 5;
        // @ts-ignore
        offsetY = window.screen.availTop + window.screenTop + 2;
      } else {
        offsetX = window.screen.width - window.screen.availWidth + window.screenLeft;
        offsetY = window.screen.height - window.screen.availHeight + window.screenTop;
      }

      /*fetch('http://localhost:18000/messages', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: target.outerHTML,
          position: {
            x: rect.left + offsetX,
            y: rect.top + offsetY
          },
          size: {
            width: rect.width,
            height: rect.height
          }
        })
      })
        .then(res => {
          console.log('Notification', 'sent', target, target.attributes);
        })
        .catch(err => {
          console.error('Notification', err, target, target.attributes);
        });*/
    });
  }
}

export default Notification;
