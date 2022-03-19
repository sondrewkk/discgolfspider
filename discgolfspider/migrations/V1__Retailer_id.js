const crypto = require("crypto")

db.discs.find().forEach(function(d){
    var id = d.url + d.brand;
    retailer_id = crypto.createHash("md5").update(id).digest("hex");
    db.discs.updateOne(
        {"_id": d._id},
        {$set: {"retailer_id": retailer_id}}
      );
  })