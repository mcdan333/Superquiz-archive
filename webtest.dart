import 'package:http/http.dart' as http;
import 'package:http/retry.dart';

void main(List<String> args) async {
  //final httpPackageUrl = Uri.https('dart.dev', '/f/packages/http.json');
  final httpPackageUrl = Uri.parse(
      'http://cdn.kingfeatures.com/rss/v1/lib/drawfeature.php?clientID=seattletimes&contentID=Superquiz&pubdate=20231118&element=body');
  final client = RetryClient(http.Client());
  try {
    final httpPackageInfo = await client.read(httpPackageUrl);
    print(httpPackageInfo.toString());
  } finally {
    client.close();
  }
}
